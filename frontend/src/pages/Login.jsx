import React from "react"
import { useState } from "react";
import { useAuth } from "../auth/AuthContext";
import { Button, Card, Input, Typography } from "antd";

export default function Login(){
  const { login } = useAuth();
  const [username,setUsername]=useState("");
  const [password,setPassword]=useState("");
  const [loading,setLoading]=useState(false);
  const [error,setError]=useState("");

  const onSubmit=async(e)=>{ e.preventDefault(); setLoading(true); setError("");
    try{ await login(username,password); window.location.href="/app"; }
    catch(err){ setError("Неверные учётные данные"); }
    finally{ setLoading(false); }
  };

  return (
    <div className="container" style={{display:"grid",placeItems:"center",height:"100%"}}>
      <Card style={{width:360}}>
        <Typography.Title level={4} style={{marginBottom:16}}>Вход</Typography.Title>
        <form onSubmit={onSubmit}>
          <div style={{display:"grid",gap:8}}>
            <Input placeholder="Логин" value={username} onChange={e=>setUsername(e.target.value)} />
            <Input.Password placeholder="Пароль" value={password} onChange={e=>setPassword(e.target.value)} />
            <Button type="primary" htmlType="submit" loading={loading}>Войти</Button>
            {error && <Typography.Text type="danger">{error}</Typography.Text>}
          </div>
        </form>
      </Card>
    </div>
  );
}
