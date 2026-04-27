
import React, { useState, useEffect } from "react";
import "./InvoicePage.css";
// import { useNavigate } from "react-router-dom";
import api from "../services/api";

const VAT_RATE = 0.2; // Example 20% VAT

const defaultProduct = { product: "", quantity: 1, price: 0 };

const statusLabels = {
  draft: "Draft",
  sent: "Sent",
  paid: "Paid",
  overdue: "Overdue",
};

export default function InvoicePage({ invoiceId }) {
  const [customer, setCustomer] = useState("");
  const [products, setProducts] = useState([{ ...defaultProduct }]);
  const [discount, setDiscount] = useState(0);
  const [status, setStatus] = useState("draft");
  const [isEditing, setIsEditing] = useState(true);
  const [pdfUrl, setPdfUrl] = useState(null);

  useEffect(() => {
    if (invoiceId) {
      // Fetch invoice data and set state
      api.get(`/invoices/${invoiceId}/`).then((res) => {
        const inv = res.data;
        setCustomer(inv.customer_name);
        setProducts(inv.products || [{ ...defaultProduct }]);
        setDiscount(inv.discount || 0);
        setStatus(inv.status);
        setIsEditing(inv.status === "draft");
      });
    }
  }, [invoiceId]);

  const handleProductChange = (idx, field, value) => {
    setProducts((prev) =>
      prev.map((p, i) => (i === idx ? { ...p, [field]: value } : p))
    );
  };

  const addProduct = () => setProducts([...products, { ...defaultProduct }]);
  const removeProduct = (idx) => setProducts(products.filter((_, i) => i !== idx));

  const subtotal = products.reduce(
    (sum, p) => sum + (parseFloat(p.price) || 0) * (parseInt(p.quantity) || 1),
    0
  );
  const vat = subtotal * VAT_RATE;
  const total = subtotal + vat - (parseFloat(discount) || 0);

  const handleSave = () => {
    const payload = {
      customer_name: customer,
      products,
      discount,
      status,
    };
    if (invoiceId) {
      api.put(`/invoices/${invoiceId}/`, payload).then(() => setIsEditing(false));
    } else {
      api.post("/invoices/", payload).then(() => setIsEditing(false));
    }
  };

  const handleSend = () => {
    setStatus("sent");
    setIsEditing(false);
    // Optionally, update status in backend
    api.patch(`/invoices/${invoiceId}/`, { status: "sent" });
  };

  const handleExportPDF = () => {
    api.get(`/invoices/${invoiceId}/export_pdf/`, { responseType: "blob" }).then((res) => {
      const url = window.URL.createObjectURL(new Blob([res.data]));
      setPdfUrl(url);
    });
  };

  return (
    <div className="invoice-page">
      <h2>{invoiceId ? "Edit Invoice" : "Create Invoice"}</h2>
      <div>
        <label>Customer Name:</label>
        <input
          value={customer}
          onChange={(e) => setCustomer(e.target.value)}
          disabled={!isEditing}
        />
      </div>
      <div>
        <label>Products:</label>
        {products.map((p, idx) => (
          <div key={idx} style={{ display: "flex", gap: 8 }}>
            <input
              placeholder="Product"
              value={p.product}
              onChange={(e) => handleProductChange(idx, "product", e.target.value)}
              disabled={!isEditing}
            />
            <input
              type="number"
              min="1"
              value={p.quantity}
              onChange={(e) => handleProductChange(idx, "quantity", e.target.value)}
              disabled={!isEditing}
            />
            <input
              type="number"
              min="0"
              value={p.price}
              onChange={(e) => handleProductChange(idx, "price", e.target.value)}
              disabled={!isEditing}
            />
            {isEditing && (
              <button onClick={() => removeProduct(idx)} disabled={products.length === 1}>
                Remove
              </button>
            )}
          </div>
        ))}
        {isEditing && <button onClick={addProduct}>Add Product</button>}
      </div>
      <div>
        <label>Discount:</label>
        <input
          type="number"
          min="0"
          value={discount}
          onChange={(e) => setDiscount(e.target.value)}
          disabled={!isEditing}
        />
      </div>
      <div>
        <strong>Subtotal:</strong> {subtotal.toFixed(2)}
      </div>
      <div>
        <strong>VAT ({VAT_RATE * 100}%):</strong> {vat.toFixed(2)}
      </div>
      <div>
        <strong>Total:</strong> {total.toFixed(2)}
      </div>
      <div>
        <strong>Status:</strong> {statusLabels[status]}
      </div>
      <div style={{ marginTop: 16 }}>
        {isEditing && <button onClick={handleSave}>Save</button>}
        {status === "draft" && !isEditing && (
          <button onClick={handleSend}>Send Invoice</button>
        )}
        {invoiceId && <button onClick={handleExportPDF}>Export PDF</button>}
        {pdfUrl && (
          <a href={pdfUrl} download={`invoice_${invoiceId}.pdf`}>
            Download PDF
          </a>
        )}
      </div>
    </div>
  );
}
