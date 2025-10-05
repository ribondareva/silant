import { Button } from "antd";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function Header({ showAuthButton = true }) {
  const nav = useNavigate();
  const { user, logout } = useAuth();
  return (
    <div className="header" style={{gap:16}}>
      {/* логотип */}
      <Link to="/" className="brand" style={{textDecoration:"none", color:"white"}}>Силант</Link>

      {/* телефон/телеграм */}
      <div style={{marginLeft:8, opacity:.9}}>+7-8352-20-12-09, telegram</div>

      {/* кнопки справа */}
      <div style={{marginLeft:"auto"}}>
        {showAuthButton && !user && (
          <Button onClick={()=>nav("/login")}>Авторизация</Button>
        )}
        {user && (
          <>
            <span style={{marginRight:8, opacity:.9}}>Вы вошли как: <b>{user.username}</b></span>
            <Button danger onClick={logout}>Выйти</Button>
          </>
        )}
      </div>
    </div>
  );
}
