import { useEffect, useState } from "react";
import api from "./axios";
import { userDisplayName } from "../utils/displayName";

export default function useServiceCompanies() {
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let mounted = true;
    (async () => {
      setLoading(true);
      try {
        const { data } = await api.get("/api/machines/", { params: { page_size: 1000 }});
        const users = new Map();
        (data.results || data).forEach(m => {
          if (m.service_company) {
            const key = m.service_company.id || m.service_company.username;
            if (!users.has(key)) users.set(key, m.service_company);
          }
        });
        const opts = Array.from(users.values())
          .map(u => ({ value: u.id || u.username, label: userDisplayName(u) }))
          .sort((a,b) => a.label.localeCompare(b.label, "ru"));
        if (mounted) setOptions(opts);
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, []);

  return { options, loading };
}
