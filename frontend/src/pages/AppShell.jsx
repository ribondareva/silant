import { useEffect, useState } from "react";
import { Tabs } from "antd";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import Header from "../components/Header";
import Footer from "../components/Footer";
import api from "../api/axios";

function displayName(u) {
  return (u?.first_name && u.first_name.trim()) || u?.username || "";
}

function roleLabel(groups = []) {
  if (groups.includes("manager")) return "Менеджер";
  if (groups.includes("service")) return "Сервисная компания";
  if (groups.includes("client"))  return "Клиент";
  return "Пользователь";
}

export default function AppShell(){
  const nav = useNavigate();
  const loc = useLocation();
  const active = loc.pathname.includes("/maintenance") ? "2"
              : loc.pathname.includes("/complaints") ? "3" : "1";

  const [me, setMe] = useState(null);
  useEffect(() => {
    (async () => {
      try {
        const { data } = await api.get("/api/profile/");
        setMe(data);
      } catch {        
        setMe({ username: localStorage.getItem("username"), first_name: "", groups: [] });
      }
    })();
  }, []);

  const titleRight = me
    ? `${roleLabel(me.groups)}: ` + displayName(me)
    : "Загрузка…";

  return (
    <>
      <Header showAuthButton={false}/>
      <div className="container">
        <div style={{ background:"white", border:"1px solid #eee", borderRadius:8, padding:12, marginBottom:12 }}>
          <div style={{ display:"flex", gap:12, flexWrap:"wrap", alignItems:"center" }}>
            <div style={{ fontWeight:600 }}>Электронная сервисная книжка «Мой Силант»</div>
            <div style={{ marginLeft:"auto", opacity:.85 }}>{titleRight}</div>
          </div>
        </div>

        <Tabs
          items={[
            { key:"1", label:"Общая инфо (Машины)" },
            { key:"2", label:"ТО" },
            { key:"3", label:"Рекламации" },
          ]}
          activeKey={active}
          onChange={(k)=>{
            if(k==="1") nav("/app/machines");
            if(k==="2") nav("/app/maintenance");
            if(k==="3") nav("/app/complaints");
          }}
        />
        <Outlet/>
      </div>
      <Footer/>
    </>
  );
}
