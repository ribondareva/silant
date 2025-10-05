import { useEffect, useState } from "react";
import { Table, Card, Input, Select, Space, Modal, Descriptions, Grid } from "antd";
import api from "../api/axios";
import useRefOptions from "../api/useRefOptions";
import useServiceCompanies from "../api/useServiceCompanies";

export default function Maintenance() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [details, setDetails] = useState(null);
  const [filters, setFilters] = useState({ kind: null, service_company: null, sn: "" });

  const kindOpts = useRefOptions("Вид ТО");
  const svcOpts  = useServiceCompanies();

  const screens = Grid.useBreakpoint();
  const full = screens.xs;

  async function load() {
    setLoading(true);
    try {
      const params = { ordering: "-performed_date" };
      if (filters.kind) params.kind = filters.kind;
      if (filters.service_company) params.service_company = filters.service_company;
      if (filters.sn) params["machine__serial_number"] = filters.sn;
      const { data } = await api.get("/api/maintenance/", { params });
      setData(data.results || data);
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => { load(); }, [JSON.stringify(filters)]);

  const columns = [
    { title: "Дата ТО", dataIndex: "performed_date" },
    { title: "Машина", dataIndex: "machine_serial" },
    { title: "Вид ТО", dataIndex: "kind_name" },
    { title: "Наработка, м/ч", dataIndex: "operating_hours" },
    {
      title: "Сервис",
      render: (_, r) => r.service_company?.first_name || r.service_company?.username || "—",
    },
  ];

  async function openDetails(record) {
    const { data } = await api.get(`/api/maintenance/${record.id}/`);
    setDetails(data);
  }

  return (
    <Card>
      <Space wrap style={{ marginBottom: 12 }}>
        <Input
          placeholder="Зав. № машины"
          style={{ width: full ? "100%" : 200 }}
          value={filters.sn}
          onChange={(e) => setFilters((f) => ({ ...f, sn: e.target.value }))}
        />
        <Select
          placeholder="Вид ТО"
          allowClear
          style={{ minWidth: full ? "100%" : 200 }}
          options={kindOpts.options}
          loading={kindOpts.loading}
          onChange={(v) => setFilters((f) => ({ ...f, kind: v }))}
        />
        <Select
          placeholder="Сервис"
          allowClear
          style={{ minWidth: full ? "100%" : 200 }}
          options={svcOpts.options}
          loading={svcOpts.loading}
          onChange={(v) => setFilters((f) => ({ ...f, service_company: v }))}
        />
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
        title={`ТО — ${details?.machine_serial || ""}`}
      >
        {details && (
          <Descriptions size="small" column={1} bordered>
            <Descriptions.Item label="Машина">{details.machine_serial}</Descriptions.Item>
            <Descriptions.Item label="Вид ТО">{details.kind_name}</Descriptions.Item>
            <Descriptions.Item label="Дата проведения">{details.performed_date}</Descriptions.Item>
            <Descriptions.Item label="Наработка, м/ч">{details.operating_hours}</Descriptions.Item>
            <Descriptions.Item label="№ заказ-наряда">{details.work_order_number || "—"}</Descriptions.Item>
            <Descriptions.Item label="Дата заказ-наряда">{details.work_order_date || "—"}</Descriptions.Item>
            <Descriptions.Item label="Организация ТО">
              {details.organization_name || details.organization?.name || "—"}
            </Descriptions.Item>
            <Descriptions.Item label="Сервисная компания">
              {details.service_company?.first_name || details.service_company?.username || "—"}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </Card>
  );
}
