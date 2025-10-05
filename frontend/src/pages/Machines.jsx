import { useEffect, useState } from "react";
import { Table, Card, Select, Space, Modal, Descriptions, Grid } from "antd";
import api from "../api/axios";
import useRefOptions from "../api/useRefOptions";
import { userDisplayName } from "../utils/displayName";

export default function Machines() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [details, setDetails] = useState(null);
  const [filters, setFilters] = useState({
    model_technique: null,
    model_engine: null,
    model_transmission: null,
    model_steer_bridge: null,
    model_drive_bridge: null,
  });

  const techOpts  = useRefOptions("Модель техники");
  const engOpts   = useRefOptions("Модель двигателя");
  const transOpts = useRefOptions("Модель трансмиссии");
  const steerOpts = useRefOptions("Модель управляемого моста");
  const driveOpts = useRefOptions("Модель ведущего моста");

  const screens = Grid.useBreakpoint();
  const full = screens.xs; // мобильный — заполняем ширину 100%

  async function load() {
    setLoading(true);
    try {
      const params = {
        ordering: "-shipment_date",
        ...Object.fromEntries(Object.entries(filters).filter(([, v]) => v)),
      };
      const { data } = await api.get("/api/machines/", { params });
      setData(data.results || data);
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => { load(); }, [JSON.stringify(filters)]);

  const columns = [
    { title: "Зав. №", dataIndex: "serial_number" },
    { title: "Модель техники", dataIndex: "model_technique_name" },
    { title: "Двигатель", dataIndex: "model_engine_name" },
    { title: "Дата отгрузки", dataIndex: "shipment_date" },
    {
      title: "Клиент",
      render: (_, r) => r.client?.first_name || r.client?.username || "—",
    },
    {
      title: "Сервис",
      render: (_, r) => r.service_company?.first_name || r.service_company?.username || "—",
    },
  ];

  async function openDetails(record) {
    const { data } = await api.get(`/api/machines/${record.id}/`);
    setDetails(data);
  }

  return (
    <Card>
      <Space style={{ marginBottom: 12 }} wrap>
        <Select placeholder="Модель техники" allowClear
          style={{ minWidth: full ? "100%" : 220 }}
          options={techOpts.options} loading={techOpts.loading}
          onChange={(v) => setFilters((f) => ({ ...f, model_technique: v }))} />
        <Select placeholder="Двигатель" allowClear
          style={{ minWidth: full ? "100%" : 220 }}
          options={engOpts.options} loading={engOpts.loading}
          onChange={(v) => setFilters((f) => ({ ...f, model_engine: v }))} />
        <Select placeholder="Трансмиссия" allowClear
          style={{ minWidth: full ? "100%" : 220 }}
          options={transOpts.options} loading={transOpts.loading}
          onChange={(v) => setFilters((f) => ({ ...f, model_transmission: v }))} />
        <Select placeholder="Упр. мост" allowClear
          style={{ minWidth: full ? "100%" : 180 }}
          options={steerOpts.options} loading={steerOpts.loading}
          onChange={(v) => setFilters((f) => ({ ...f, model_steer_bridge: v }))} />
        <Select placeholder="Вед. мост" allowClear
          style={{ minWidth: full ? "100%" : 180 }}
          options={driveOpts.options} loading={driveOpts.loading}
          onChange={(v) => setFilters((f) => ({ ...f, model_drive_bridge: v }))} />
      </Space>

      <Table
        rowKey="id"
        loading={loading}
        columns={columns}
        dataSource={data}
        onRow={(record) => ({ onClick: () => openDetails(record), style: { cursor: "pointer" } })}
        scroll={{ x: true }}
        size="middle"
      />

      <Modal
        open={!!details}
        onCancel={() => setDetails(null)}
        footer={null}
        width={"min(720px, 92vw)"}
        bodyStyle={{ overflowX: "auto" }}
        title={`Машина ${details?.serial_number || ""}`}
      >
        {details && (
          <Descriptions size="small" column={1} bordered>
            <Descriptions.Item label="Модель техники">{details.model_technique_name}</Descriptions.Item>
            <Descriptions.Item label="Модель двигателя">{details.model_engine_name}</Descriptions.Item>
            <Descriptions.Item label="Модель трансмиссии">{details.model_transmission_name}</Descriptions.Item>
            <Descriptions.Item label="Модель ведущего моста">{details.model_drive_bridge_name}</Descriptions.Item>
            <Descriptions.Item label="Модель управляемого моста">{details.model_steer_bridge_name}</Descriptions.Item>
            <Descriptions.Item label="Дата отгрузки">{details.shipment_date}</Descriptions.Item>
            <Descriptions.Item label="Покупатель (клиент)">{userDisplayName(details.client)}</Descriptions.Item>
            <Descriptions.Item label="Сервисная компания">
              {details.service_company?.first_name || details.service_company?.username || "—"}
            </Descriptions.Item>
            <Descriptions.Item label="Комплектация">{details.equipment || "—"}</Descriptions.Item>
            <Descriptions.Item label="Адрес поставки">{details.delivery_address || "—"}</Descriptions.Item>
            <Descriptions.Item label="Грузополучатель">{details.consignee || "—"}</Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </Card>
  );
}
