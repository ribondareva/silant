import { useEffect, useState } from "react";
import { Table, Card, Select, Space, Input, Modal, Descriptions, Grid } from "antd";
import api from "../api/axios";
import useRefOptions from "../api/useRefOptions";
import useServiceCompanies from "../api/useServiceCompanies";

export default function Complaints() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [details, setDetails] = useState(null);
  const [filters, setFilters] = useState({
    failure_node: null,
    recovery_method: null,
    service_company: null,
    sn: "",
  });

  const nodeOpts   = useRefOptions("Узел отказа");
  const methodOpts = useRefOptions("Способ восстановления");
  const svcOpts    = useServiceCompanies();

  const screens = Grid.useBreakpoint();
  const full = screens.xs;

  async function load() {
    setLoading(true);
    try {
      const params = { ordering: "-failure_date" };
      if (filters.failure_node) params.failure_node = filters.failure_node;
      if (filters.recovery_method) params.recovery_method = filters.recovery_method;
      if (filters.service_company) params.service_company = filters.service_company;
      if (filters.sn) params["machine__serial_number"] = filters.sn;
      const { data } = await api.get("/api/complaints/", { params });
      setData(data.results || data);
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => { load(); }, [JSON.stringify(filters)]);

  const columns = [
    { title: "Дата отказа", dataIndex: "failure_date" },
    { title: "Машина", dataIndex: "machine_serial" },
    { title: "Узел отказа", dataIndex: "failure_node_name" },
    { title: "Способ восстановления", dataIndex: "recovery_method_name" },
    {
      title: "Сервис",
      render: (_, r) => r.service_company?.first_name || r.service_company?.username || "—",
    },
  ];

  async function openDetails(record) {
    const { data } = await api.get(`/api/complaints/${record.id}/`);
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
          placeholder="Узел отказа"
          allowClear
          style={{ minWidth: full ? "100%" : 220 }}
          options={nodeOpts.options}
          loading={nodeOpts.loading}
          onChange={(v) => setFilters((f) => ({ ...f, failure_node: v }))}
        />
        <Select
          placeholder="Способ восстановления"
          allowClear
          style={{ minWidth: full ? "100%" : 220 }}
          options={methodOpts.options}
          loading={methodOpts.loading}
          onChange={(v) => setFilters((f) => ({ ...f, recovery_method: v }))}
        />
        <Select
          placeholder="Сервисная компания"
          allowClear
          style={{ minWidth: full ? "100%" : 220 }}
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
        title={`Рекламация — ${details?.machine_serial || ""}`}
      >
        {details && (
          <Descriptions size="small" column={1} bordered>
            <Descriptions.Item label="Машина">{details.machine_serial}</Descriptions.Item>
            <Descriptions.Item label="Дата отказа">{details.failure_date}</Descriptions.Item>
            <Descriptions.Item label="Наработка, м/ч">{details.operating_hours}</Descriptions.Item>
            <Descriptions.Item label="Узел отказа">{details.failure_node_name}</Descriptions.Item>
            <Descriptions.Item label="Описание отказа">{details.failure_description || "—"}</Descriptions.Item>
            <Descriptions.Item label="Способ восстановления">{details.recovery_method_name}</Descriptions.Item>
            <Descriptions.Item label="Запасные части">{details.parts_used || "—"}</Descriptions.Item>
            <Descriptions.Item label="Дата восстановления">{details.recovery_date || "—"}</Descriptions.Item>
            <Descriptions.Item label="Время простоя, дни">{details.downtime_days ?? "—"}</Descriptions.Item>
            <Descriptions.Item label="Сервисная компания">
              {details.service_company?.first_name || details.service_company?.username || "—"}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </Card>
  );
}
