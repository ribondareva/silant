from django.core.management.base import BaseCommand, CommandParser
from django.contrib.auth.models import User, Group
from django.utils.text import slugify
from django.db import transaction
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Optional
import re
import pandas as pd

from silant.models import Reference, Machine, Maintenance, Complaint


def norm_val(s):
    if pd.isna(s):
        return ""
    return str(s).strip()


def parse_date(v):
    if v is None or (isinstance(v, float) and pd.isna(v)) or (isinstance(v, str) and not v.strip()):
        return None

    if hasattr(v, "to_pydatetime"):
        v = v.to_pydatetime()
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v

    s = str(v).strip()

    if " " in s:
        s_first = s.split(" ")[0]
    else:
        s_first = s

    # 1) обычные форматы
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y", "%d.%m.%y"):
        try:
            return datetime.strptime(s_first, fmt).date()
        except Exception:
            pass

    # 2) ISO с временем
    try:
        return datetime.fromisoformat(s).date()
    except Exception:
        pass

    # 3) серийник Excel (например "44625" или "44625.0")
    try:
        num = float(s.replace(",", "."))
        if 20000 <= num <= 80000:
            base = datetime(1899, 12, 30)
            return (base + timedelta(days=num)).date()
    except Exception:
        pass

    return None


def norm_col(s: str) -> str:
    """приводим имя столбца к нормализованному виду"""
    s = str(s).lower()
    s = s.replace("№", "номер")
    s = re.sub(r"[\(\)\.,/\\\-]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def find_col(df: pd.DataFrame, *candidates) -> Optional[str]:
    """ищем колонку по набору кандидатов"""
    cols = {norm_col(c): c for c in df.columns}
    cand_norm = [norm_col(c) for c in candidates]
    # точное совпадение
    for cn in cand_norm:
        if cn in cols:
            return cols[cn]
    for cn in cand_norm:
        keys = cn.split()
        for norm_name, original in cols.items():
            if all(k in norm_name for k in keys):
                return original
    return None


def ref(entity: str, name):
    name = norm_val(name)
    if not name:
        return None
    return Reference.objects.get_or_create(entity=entity, name=name)[0]


def get_or_create_user(name, group_name: str) -> Optional[User]:
    name = norm_val(name)
    if not name:
        return None

    # 1) транслитерирует кириллицу → латиницу
    base = slugify(name)  # "ООО 'ФПК21'" -> "ooo-fpk21"

    # 2) запасные варианты, если вдруг пусто
    if not base:
        base = group_name
    base = base.strip("._-") or group_name

    # 3) гарантированная уникальность
    username = base
    i = 2
    while User.objects.filter(username=username).exists():
        username = f"{base}-{i}"
        i += 1

    user = User.objects.filter(username=username).first()
    if not user:
        user = User.objects.create_user(username=username, password="changeme123", is_active=True)
        grp, _ = Group.objects.get_or_create(name=group_name)
        user.groups.add(grp)
        user.save()
    return user


def read_sheet(path: str, sheet: str, header_hint: Optional[int]) -> pd.DataFrame:
    """
    Читает лист Excel. Если header_hint задан (1-based) — используем его.
    Иначе пытаемся autodetect в первых 10 строках.
    """
    if header_hint:
        hdr = int(header_hint) - 1  # 1-based -> 0-based
        return pd.read_excel(path, sheet_name=sheet, header=hdr, dtype=str, engine="openpyxl")

    raw = pd.read_excel(path, sheet_name=sheet, header=None, dtype=str, engine="openpyxl")
    anchors = ("модель техники", "зав", "машин", "вид то", "дата отказа", "дата проведения то")
    hdr = 0
    for i in range(min(10, len(raw.index))):
        row_text = " ".join(str(x).lower() for x in raw.iloc[i].tolist() if pd.notna(x))
        if any(a in row_text for a in anchors):
            hdr = i
            break
    return pd.read_excel(path, sheet_name=sheet, header=hdr, dtype=str, engine="openpyxl")


class Command(BaseCommand):
    help = "Импорт из Excel: машины, ТО, рекламации"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("path", help="Путь к .xlsx")

        # названия листов
        parser.add_argument("--machines", default="машины")
        parser.add_argument("--to", default="ТО output")
        parser.add_argument("--claims", default="рекламация output")

        # строка заголовков (1-based)
        parser.add_argument("--hdr-machines", type=int, default=None, help="Строка заголовков листа 'машины' (1-based)")
        parser.add_argument("--hdr-to", type=int, default=None, help="Строка заголовков листа 'ТО output' (1-based)")
        parser.add_argument("--hdr-claims", type=int, default=None, help="Строка заголовков листа 'рекламация output' (1-based)")

        # сервисная компания по умолчанию (username)
        parser.add_argument("--service", default=None, help="username сервисной компании по умолчанию")

    @transaction.atomic
    def handle(self, path, machines, to, claims, hdr_machines, hdr_to, hdr_claims, service, **_):
        path = str(Path(path))
        self.stdout.write(self.style.NOTICE(f"Читаю файл: {path}"))

        # сервисная компания по умолчанию
        default_service = User.objects.filter(username=service).first() if service else None
        if service and not default_service:
            default_service = User.objects.create_user(username=service, password="changeme123", is_active=True)
            g, _ = Group.objects.get_or_create(name="service")
            default_service.groups.add(g)

        # ---------- МАШИНЫ ----------
        try:
            df_m = read_sheet(path, machines, hdr_machines)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Не удалось открыть лист '{machines}': {e}"))
            df_m = None

        if df_m is not None:
            c_serial              = find_col(df_m, "зав. номер машины")
            c_model_technique     = find_col(df_m, "модель техники")
            c_model_engine        = find_col(df_m, "модель двигателя")
            c_serial_engine       = find_col(df_m, "зав. номер двигателя")
            c_model_transmission  = find_col(df_m, "модель трансмиссии производитель артикул", "модель трансмиссии")
            c_serial_transmission = find_col(df_m, "зав. номер трансмиссии")
            c_model_drive_bridge  = find_col(df_m, "модель ведущего моста")
            c_serial_drive_bridge = find_col(df_m, "зав. номер ведущего моста")
            c_model_steer_bridge  = find_col(df_m, "модель управляемого моста")
            c_serial_steer_bridge = find_col(df_m, "зав. номер управляемого моста")
            c_shipment_date       = find_col(df_m, "дата отгрузки с завода")
            c_client_name         = find_col(df_m, "покупатель", "клиент")
            c_consignee           = find_col(df_m, "грузополучатель конечный потребитель")
            c_delivery_address    = find_col(df_m, "адрес поставки эксплуатации")
            c_equipment           = find_col(df_m, "комплектация доп опции", "комплектация")
            c_contract            = find_col(df_m, "договор поставки номер дата", "договор")
            c_service_company     = find_col(df_m, "сервисная компания")

            created, updated = 0, 0
            for _, row in df_m.iterrows():
                sn = norm_val(row.get(c_serial))
                if not sn:
                    continue

                mt = ref("Модель техники",            row.get(c_model_technique))
                me = ref("Модель двигателя",          row.get(c_model_engine))
                tr = ref("Модель трансмиссии",        row.get(c_model_transmission))
                db = ref("Модель ведущего моста",     row.get(c_model_drive_bridge))
                sb = ref("Модель управляемого моста", row.get(c_model_steer_bridge))

                client_user  = get_or_create_user(row.get(c_client_name), "client") if c_client_name else None
                service_user = get_or_create_user(row.get(c_service_company), "service") if c_service_company else default_service

                _, was_created = Machine.objects.update_or_create(
                    serial_number=sn,
                    defaults=dict(
                        model_technique=mt,
                        model_engine=me,
                        model_transmission=tr,
                        model_drive_bridge=db,
                        model_steer_bridge=sb,
                        serial_engine=norm_val(row.get(c_serial_engine)),
                        serial_transmission=norm_val(row.get(c_serial_transmission)),
                        serial_drive_bridge=norm_val(row.get(c_serial_drive_bridge)),
                        serial_steer_bridge=norm_val(row.get(c_serial_steer_bridge)),
                        shipment_date=parse_date(row.get(c_shipment_date)),
                        consignee=norm_val(row.get(c_consignee)),
                        delivery_address=norm_val(row.get(c_delivery_address)),
                        equipment=norm_val(row.get(c_equipment)),
                        contract_number=norm_val(row.get(c_contract)) if c_contract else "",
                        client=client_user,
                        service_company=service_user,
                    ),
                )
                created += int(was_created)
                updated += int(not was_created)
            self.stdout.write(self.style.SUCCESS(f"Машины: создано {created}, обновлено {updated}"))

        # ---------- ТО ----------
        try:
            df_to = read_sheet(path, to, hdr_to)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Не удалось открыть лист '{to}': {e}"))
            df_to = None

        if df_to is not None:
            c_sn       = find_col(df_to, "зав. номер машины")
            c_kind     = find_col(df_to, "вид то")
            c_date     = find_col(df_to, "дата проведения то")
            c_hours    = find_col(df_to, "наработка м час", "наработка")
            c_wo_no    = find_col(df_to, "номер заказ-наряда")
            c_wo_date  = find_col(df_to, "дата заказ-наряда")
            c_org      = find_col(df_to, "организация проводившая то")

            cnt = 0
            for _, row in df_to.iterrows():
                sn = norm_val(row.get(c_sn))
                if not sn:
                    continue
                machine = Machine.objects.filter(serial_number=sn).first()
                if not machine:
                    continue

                Maintenance.objects.get_or_create(
                    machine=machine,
                    kind=ref("Вид ТО", row.get(c_kind)),
                    performed_date=parse_date(row.get(c_date)),
                    defaults=dict(
                        operating_hours=int(float(norm_val(row.get(c_hours) or "0"))),
                        work_order_number=norm_val(row.get(c_wo_no)),
                        work_order_date=parse_date(row.get(c_wo_date)),
                        organization=ref("Организация ТО", row.get(c_org)),
                        service_company=machine.service_company or default_service,
                    ),
                )
                cnt += 1
            self.stdout.write(self.style.SUCCESS(f"ТО: загружено {cnt} записей"))

        # ---------- Рекламации ----------
        try:
            df_c = read_sheet(path, claims, hdr_claims)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Не удалось открыть лист '{claims}': {e}"))
            df_c = None

        if df_c is not None:
            c_sn       = find_col(df_c, "зав. номер")   # «Зав. №»
            c_fail_dt  = find_col(df_c, "дата отказа")
            c_hours    = find_col(df_c, "наработка")    # «наработка, ...»
            c_node     = find_col(df_c, "узел отказа")
            c_descr    = find_col(df_c, "описание отказа")
            c_method   = find_col(df_c, "способ")       # «способ восстановления»
            c_parts    = find_col(df_c, "используемые")
            c_rec_dt   = find_col(df_c, "дата")         # дата восстановления
            c_down     = find_col(df_c, "время")        # время простоя, дни (опц.)

            cnt = 0
            for _, row in df_c.iterrows():
                sn = norm_val(row.get(c_sn))
                if not sn:
                    continue
                machine = Machine.objects.filter(serial_number=sn).first()
                if not machine:
                    continue

                obj, _ = Complaint.objects.get_or_create(
                    machine=machine,
                    failure_date=parse_date(row.get(c_fail_dt)),
                    failure_node=ref("Узел отказа", row.get(c_node)),
                    defaults=dict(
                        operating_hours=int(float(norm_val(row.get(c_hours) or "0"))),
                        failure_description=norm_val(row.get(c_descr)),
                        recovery_method=ref("Способ восстановления", row.get(c_method)),
                        parts_used=norm_val(row.get(c_parts)),
                        recovery_date=parse_date(row.get(c_rec_dt)),
                        service_company=machine.service_company or default_service,
                    ),
                )
                # если в файле есть "Время", подставим
                try:
                    days = int(float(norm_val(row.get(c_down)))) if c_down else None
                    if days is not None and obj.downtime_days != days:
                        obj.downtime_days = max(0, days)
                        obj.save(update_fields=["downtime_days"])
                except Exception:
                    pass
                cnt += 1
            self.stdout.write(self.style.SUCCESS(f"Рекламации: загружено {cnt} записей"))
