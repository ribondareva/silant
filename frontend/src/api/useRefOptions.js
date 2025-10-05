import { useEffect, useState, useCallback } from "react";
import api from "./axios";

/**
 * подгружает элементы справочника и отдаёт options для <Select/>.
 * entity — точное имя справочника (как в БД): например "Вид ТО", "Узел отказа", "Модель техники" и т.п.
 */
export default function useRefOptions(entity) {
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    if (!entity) return;
    setLoading(true);
    setError("");
    try {   
      let url = "/api/references/";
      const params = { entity, ordering: "name", page_size: 100 };
      let items = [];
      let { data } = await api.get(url, { params });
      if (Array.isArray(data)) {
        items = data;
      } else {
        items = data.results || [];
        while (data.next) {
          const nextUrl = new URL(data.next);
          const query = Object.fromEntries(nextUrl.searchParams.entries());
          const { data: more } = await api.get(url, { params: query });
          items = items.concat(more.results || []);
          data = more;
        }
      }

      setOptions(items.map(i => ({ label: i.name, value: i.id, raw: i })));
    } catch (e) {
      setError("Не удалось загрузить справочник");
      setOptions([]);
    } finally {
      setLoading(false);
    }
  }, [entity]);

  useEffect(() => { load(); }, [load]);

  return { options, loading, error, reload: load };
}
