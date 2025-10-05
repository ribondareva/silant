import React from "react"
import { useState } from "react";
import api from "../api/axios";
import { Card, Input, Button, Table, Typography } from "antd";
import Header from "../components/Header";
import Footer from "../components/Footer";

export default function PublicLookup(){
  const [serial,setSerial]=useState("");
  const [row,setRow]=useState(null);
  const [loading,setLoading]=useState(false);
  const [error,setError]=useState("");

  async function search(){
    if(!serial.trim()) return;
    setLoading(true); setError(""); setRow(null);
    try{
      const { data } = await api.get("/api/public/machine-by-serial/", { params:{ serial }});
      setRow(data);
    }catch(e){
      setError(e?.response?.data?.detail || "Данных о машине с таким номером нет в системе");
    }finally{ setLoading(false); }
  }

  const columns = [
    { title:"Модель техники", dataIndex:"model_technique_name" },
    { title:"Зав. № машины", dataIndex:"serial_number" },
    { title:"Модель двигателя", dataIndex:"model_engine_name" },
    { title:"Зав. № двигателя", dataIndex:"serial_engine" },
    { title:"Модель трансмиссии", dataIndex:"model_transmission_name" },
    { title:"Зав. № трансмиссии", dataIndex:"serial_transmission" },
    { title:"Модель ведущего моста", dataIndex:"model_drive_bridge_name" },
    { title:"Зав. № ведущего моста", dataIndex:"serial_drive_bridge" },
    { title:"Модель управляемого моста", dataIndex:"model_steer_bridge_name" },
    { title:"Зав. № управляемого моста", dataIndex:"serial_steer_bridge" },
  ];

  return (
    <>
      <Header showAuthButton />
      <div className="container" style={{maxWidth:980, display:"grid", gap:16}}>
        <Card>
          <Typography.Title level={5} style={{marginTop:0}}>
            Электронная сервисная книжка «Мой Силант»
          </Typography.Title>
        </Card>

        <Card>
          <Typography.Paragraph>
            Проверьте комплектацию и технические характеристики техники «Силант».
          </Typography.Paragraph>

          <div style={{display:"flex", gap:8}}>
            <Input placeholder="Заводской номер" value={serial}
                   onChange={e=>setSerial(e.target.value)}
                   onPressEnter={search}/>
            <Button type="primary" onClick={search} loading={loading}>Поиск</Button>
          </div>

          <div style={{marginTop:16}}>
            <Typography.Text type="secondary">
              Информация о комплектации и технических характеристиках вашей техники
            </Typography.Text>
          </div>

          {error && <Typography.Text type="danger" style={{display:"block",marginTop:12}}>{error}</Typography.Text>}
        </Card>

        {row && (
          <Card>
            <Table columns={columns} dataSource={[row]} pagination={false} rowKey="serial_number"/>
          </Card>
        )}
      </div>
      <Footer/>
    </>
  );
}
