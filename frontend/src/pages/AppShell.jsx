import React from "react"
import { useEffect, useState } from "react";
import { Tabs } from "antd";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import Header from "../components/Header";
import Footer from "../components/Footer";
import api from "../api/axios";

function displayName(u) {
  return (u?.first_name && u.first_name.trim()) || u?.username || "";
}

// учитываем активную роль из localStorage
function roleLabel(groups = [], active) {
  const g =
    active ||
    (groups?.includes("manager")
      ? "manager"
      : groups?.includes("service")
      ? "service"
      : groups?.includes("client")
      ? "client"
      : null);
  if (g === "manager") return "Менеджер";
  if (g === "service") return "Сервисная компания";
  if (g === "client") return "Клиент";
  return "Пользователь";
}

export default function AppShell() {
  const nav = useNavigate();
  const loc = useLocation();
  const activeTab = loc.pathname.includes("/maintenance")
    ? "2"
    : loc.pathname.includes("/complaints")
    ? "3"
    : "1";

  const [me, setMe] = useState(null);
  const [activeRole, setActiveRole] = useState(
    localStorage.getItem("active_role")
  );

  useEffect(() => {
    (async () => {
      try {
        const { data } = await api.get("/api/auth/me/");
        setMe(data);

        // если роль ещё не выбрана — выберем первую доступную
        if (!localStorage.getItem("active_role")) {
          const g = data.groups || [];
          const pref = g.includes("manager")
            ? "manager"
            : g.includes("service")
            ? "service"
            : g.includes("client")
            ? "client"
            : null;
          if (pref) {
            localStorage.setItem("active_role", pref);
            setActiveRole(pref);
          }
        }
      } catch {
        setMe(null); // гость
      }
    })();
  }, []);

  const titleRight = me
    ? `${roleLabel(me.groups, activeRole)}: ` + displayName(me)
    : "Гость";

  // небольшой переключатель роли (только те, что доступны юзеру)
  function canUse(role) {
    return me?.groups?.includes(role);
  }
  function pick(role) {
    if (!canUse(role)) return;
    localStorage.setItem("active_role", role);
    setActiveRole(role);
    // при необходимости можно обновить текущие списки
    // например: invalidate queries / перезагрузить страницу
  }

  return (
    <>
      <Header showAuthButton={false} />
      <div className="container">
        <div
          style={{
            background: "white",
            border: "1px solid #eee",
            borderRadius: 8,
            padding: 12,
            marginBottom: 12,
          }}
        >
          <div
            style={{
              display: "flex",
              gap: 12,
              flexWrap: "wrap",
              alignItems: "center",
            }}
          >
            <div style={{ fontWeight: 600 }}>
              Электронная сервисная книжка «Мой Силант»
            </div>

            <div
              style={{
                marginLeft: "auto",
                opacity: 0.9,
                display: "flex",
                gap: 8,
                alignItems: "center",
              }}
            >
              <span>{titleRight}</span>
              {me && (
                <div style={{ display: "flex", gap: 6 }}>
                  {["manager", "service", "client"].map(
                    (r) =>
                      canUse(r) && (
                        <button
                          key={r}
                          onClick={() => pick(r)}
                          style={{
                            padding: "2px 8px",
                            borderRadius: 6,
                            border: "1px solid #ddd",
                            background:
                              activeRole === r ? "#EBE6D6" : "white",
                            cursor: "pointer",
                          }}
                        >
                          {r === "manager"
                            ? "Менеджер"
                            : r === "service"
                            ? "Сервис"
                            : "Клиент"}
                        </button>
                      )
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* вкладки можно показывать только авторизованным */}
        {me && (
          <Tabs
            items={[
              { key: "1", label: "Общая инфо (Машины)" },
              { key: "2", label: "ТО" },
              { key: "3", label: "Рекламации" },
            ]}
            activeKey={activeTab}
            onChange={(k) => {
              if (k === "1") nav("/app/machines");
              if (k === "2") nav("/app/maintenance");
              if (k === "3") nav("/app/complaints");
            }}
          />
        )}
        <Outlet />
      </div>
      <Footer />
    </>
  );
}
