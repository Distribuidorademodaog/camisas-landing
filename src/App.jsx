import { useState, useEffect } from 'react';
import emailjs from '@emailjs/browser';

import modelo from './assets/camisas.jpg';
import modelo2 from './assets/camisa2.jpg';
import tabla from './assets/tabla.jpg';
import uno from './assets/1camisa.png';
import tres from './assets/3camisas.png';
import seis from './assets/6camisas.png';
import oferta from './assets/oferta.png';


// Colores
import amarillo from './assets/camisas/camisa-amarillo.jpg';
import azulclaro from './assets/camisas/camisa-azulclaro.jpg';
import verdemilitar from './assets/camisas/camisa-verdemilitar.jpg';
import rojo from './assets/camisas/camisa-rojo.jpg';
import azulmedio from './assets/camisas/camisa-azulmedio.jpg';
import blanco from './assets/camisas/camisa-blanco.jpg';
import negro from './assets/camisas/camisa-negro.jpg';
import verde from './assets/camisas/camisa-verde.jpg';
import rosada from './assets/camisas/camisa-rosada.jpg';
import bossazul from './assets/camisas/boss-azul.jpg';
import cuadrosamarillo from './assets/camisas/cuadros-amarillo.jpg'; // Nueva imagen
import videoCamisas from './assets/video-camisas.mp4';


const tallas = ["S", "M", "L", "XL", "XXL", "3XL"];

const colores = [
  { nombre: "Negro", img: negro },
  { nombre: "Blanco", img: blanco },
  { nombre: "rojo", img: rojo },
  { nombre: "Azul claro", img: azulclaro },
  { nombre: "Azul medio", img: azulmedio },
  { nombre: "Verde militar", img: verdemilitar },
  { nombre: "Verde", img: verde },
  { nombre: "rosada", img: rosada },
  { nombre: "Amarillo", img: amarillo },
  { nombre: "Boss azul", img: bossazul },
  { nombre: "cuadros Amarillo", img: cuadrosamarillo },
  
];

export default function App() {
  const [step, setStep] = useState(1);
  const [cantidad, setCantidad] = useState(1);
  const [camisas, setCamisas] = useState([{ color: "", talla: "" }]);
  const [datos, setDatos] = useState({ nombre: "", cedula: "", ciudad: "", direccion: "", barrio: "", celular: "", correo: "" });
  const [tiempoRestante, setTiempoRestante] = useState(73800); // 20h 30m = 73800 segundos
  const [imagenAmpliada, setImagenAmpliada] = useState(null); // NUEVO: para ampliar imágenes

  useEffect(() => {
    const timer = setInterval(() => {
      setTiempoRestante(prev => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatoTiempo = (segundos) => {
    const h = Math.floor(segundos / 3600);
    const m = Math.floor((segundos % 3600) / 60);
    const s = segundos % 60;
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const handlePackSelect = (n) => {
    setCantidad(n);
    setCamisas(Array(n).fill({ color: "", talla: "" }));
    setStep(2);
  };

  const handleCamisaChange = (index, field, value) => {
    const nuevas = [...camisas];
    nuevas[index] = { ...nuevas[index], [field]: value };
    setCamisas(nuevas);
  };

  const handleDatosChange = (field, value) => {
    setDatos({ ...datos, [field]: value });
  };

  const obtenerImagenColor = (nombreColor) => {
    const encontrado = colores.find((c) => c.nombre === nombreColor);
    return encontrado ? encontrado.img : null;
  };

  const handleSubmit = () => {
    const celularSoloNumeros = datos.celular.replace(/\D/g, '');
const celularValido = celularSoloNumeros.length === 10;
    const nombreValido = datos.nombre.trim().length > 0;
  
    if (!nombreValido || !celularValido) {
      return; // No envía si nombre está vacío o celular no tiene 10 dígitos
    }
  
    const templateParams = {
      nombre: datos.nombre,
      cedula: datos.cedula,
      ciudad: datos.ciudad,
      direccion: datos.direccion,
      barrio: datos.barrio,
      celular: datos.celular,
      correo: datos.correo,
      cantidad,
      detalle: camisas.map((c, i) => `Camisa ${i + 1}: ${c.color} - ${c.talla}`).join("\n"),
    };
  
    emailjs.send('service_6ky78ug', 'template_gjb5ogc', templateParams, 'U0jIWruEWKvne7-ss')
    .then(() => {
  // Enviar a EmailJS fue exitoso, ahora enviamos al webhook
  fetch("https://contactos.xn--cuellosypuos-jhb.com/webhook-pedido", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      name: datos.nombre,
      phone: "+57" + datos.celular,
      email: datos.correo
      detalle: camisas.map((c, i) => `Camisa ${i + 1}: ${c.color} - ${c.talla}`).join("\n")
    })
  }).then(() => {
    if (window.fbq) {
      fbq('track', 'Purchase');
    }
    setStep(4);
  }).catch((error) => {
    console.error("Error al enviar al webhook:", error);
    setStep(4); // Igual avanza al paso 4
  });
})

      .catch((error) => {
        console.error("Error enviando el correo:", error);
        alert("Hubo un problema al enviar el pedido.");
      });
  };

  return (
    <div className="container" style={{ padding: 20, fontFamily: 'sans-serif', maxWidth: 900, margin: "0 auto" }}>
      {step === 1 && (
        <>
          <h1 style={{ fontSize: "2rem", fontWeight: "bold" }}>Haz tu pedido fácil y rápido</h1>

<div
  style={{
    display: "flex",
    flexWrap: "wrap",
    justifyContent: "center",
    gap: 12,
    marginTop: 10,
  }}
>
  <img
    src={modelo}
    alt="Camisas"
    style={{
      width: "100%",
      maxWidth: 220,
      objectFit: "contain",
      borderRadius: 8,
    }}
  />
  
  <img
    src={modelo2}
    alt="Camisas 2"
    style={{
      width: "100%",
      maxWidth: 220,
      objectFit: "contain",
      borderRadius: 8,
    }}
  />
</div>

          
          <div style={{ backgroundColor: "#001f3f", color: "white", margin: "25px 0", padding: 12, borderRadius: 6, textAlign: "center" }}>
            <h2 style={{ margin: 0 }}>Pago contraentrega</h2>
          </div>

          {/* Imágenes de colores */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(90px, 1fr))", gap: 15 }}>
            {colores.map((c, idx) => (
              <div key={idx} style={{ textAlign: "center" }}>
                <img
                  src={c.img}
                  alt={c.nombre}
                  onClick={() => setImagenAmpliada(c.img)}
                  style={{ width: 60, height: 60, objectFit: "cover", borderRadius: 6, border: "1px solid #ccc", cursor: "pointer" }}
                />
                <div style={{ fontSize: 12, marginTop: 5 }}>{c.nombre}</div>
              </div>
            ))}
          </div>

          {/* Video demostrativo */}
<div style={{ margin: "30px 0", textAlign: "center" }}>
  <video
    src={videoCamisas}
    controls
    autoPlay
    muted
    loop
    style={{ width: "100%", maxWidth: "400px", borderRadius: 10 }}
  />
</div>

          <div style={{ backgroundColor: "#001f3f", padding: 12, borderRadius: 6, margin: "20px 0", color: "#fff", textAlign: "center" }}>
            <h2 style={{ margin: 0 }}>Selecciona un pack</h2>
          </div>

          <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: 15 }}>
            {[{ img: uno, cant: 1 }, { img: tres, cant: 3 }, { img: seis, cant: 6 }].map((pack, index) => (
              <div key={index} onClick={() => handlePackSelect(pack.cant)} style={{ maxWidth: 200, cursor: "pointer", textAlign: "center" }}>
                <img src={pack.img} alt={`${pack.cant} camisas`} style={{ width: "100%", borderRadius: 10 }} />
                <button style={{ marginTop: 8, backgroundColor: "#001f3f", color: "#fff", padding: "6px 12px", border: "none", borderRadius: 6 }}>
                  Seleccionar
                </button>
              </div>
            ))}
          </div>



          {/* Contador regresivo */}
          <div style={{ textAlign: "center", fontSize: "1.4rem", fontWeight: "bold", margin: "30px 0", color: "#001f3f" }}>
            Oferta finaliza en: <span style={{ background: "#001f3f", color: "#fff", padding: "8px 16px", borderRadius: 8 }}>{formatoTiempo(tiempoRestante)}</span>
          </div>

          {/* Oferta + tabla */}
          <div style={{ display: "flex", flexWrap: "wrap", gap: "20px", alignItems: "stretch", justifyContent: "center" }}>
            <img src={oferta} alt="Oferta por tiempo limitado" style={{ width: "100%", maxWidth: 320, borderRadius: 10 }} />
            <div style={{ backgroundColor: "#001f3f", color: "white", padding: 20, borderRadius: 10, maxWidth: 320 }}>
              <p><strong>• 98% Algodón</strong></p>
              <p><strong>• Calidad Premium</strong></p>
              <p><strong>• Tallas de la S a la XXXL</strong></p>
              <p><strong>• Tallaje normal</strong></p>
              <p><strong>• Cambios por tallas</strong></p>
              <p><strong>• Garantía de 30 días por imperfectos</strong></p>
            </div>
          </div>
        </>
      )}

{step === 2 && (
  <div>
  
    {/* Miniaturas de referencia de todos los colores */}
    <div style={{ marginTop: 30 }}>
      <h3 style={{ marginBottom: 10 }}>Colores disponibles:</h3>
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(90px, 1fr))",
        gap: 15,
        justifyItems: "center"
      }}>
        {colores.map((c, idx) => (
          <div key={idx} style={{ textAlign: "center" }}>
            <img
              src={c.img}
              alt={c.nombre}
              style={{ width: 60, height: 60, objectFit: "cover", borderRadius: 6, border: "1px solid #ccc", cursor: "pointer" }}
              onClick={() => setImagenAmpliada(c.img)}
            />
            <div style={{ fontSize: 12, marginTop: 5 }}>
  <strong>{idx + 1}.</strong> {c.nombre}
</div>
          </div>
        ))}
      </div>
    </div>

    <h2>Selecciona color y talla</h2>

{camisas.map((camisa, i) => {
  const imagenColor = obtenerImagenColor(camisa.color);
  return (
    <div key={i} style={{ marginBottom: 30 }}>
      <p>Camisa {i + 1}</p>
      <select onChange={(e) => handleCamisaChange(i, 'color', e.target.value)}>
  <option value="">Selecciona color</option>
  {colores.map((c, index) => (
    <option key={c.nombre} value={c.nombre}>
      {index + 1}. {c.nombre}
    </option>
  ))}
</select>
      <select onChange={(e) => handleCamisaChange(i, 'talla', e.target.value)} style={{ marginLeft: 10 }}>
        <option value="">Selecciona talla</option>
        {tallas.map((t) => <option key={t}>{t}</option>)}
      </select>

      {/* Vista previa del color seleccionado */}
      {camisa.color && imagenColor && (
  <div style={{ marginTop: 10 }}>
    <img
      src={imagenColor}
      alt={camisa.color}
      style={{ width: 80, height: 80, objectFit: "cover", borderRadius: 6, cursor: "pointer" }}
      onClick={() => setImagenAmpliada(imagenColor)}
    />
    <p style={{ fontSize: 14 }}>{camisa.color}</p>
  </div>
)}
    </div>
  );
})}

    {/* Imagen ampliada (lightbox) */}
    {imagenAmpliada && (
      <div
        onClick={() => setImagenAmpliada(null)}
        style={{
          position: "fixed",
          top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: "rgba(0,0,0,0.7)",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          zIndex: 9999
        }}
      >
        <img
          src={imagenAmpliada}
          alt="Vista ampliada"
          style={{ maxWidth: "90%", maxHeight: "90%", borderRadius: 10 }}
        />
      </div>
    )}
<div style={{ display: "flex", justifyContent: "space-between", marginTop: 20 }}>
      <button onClick={() => setStep(1)}>Atrás</button>
      <button onClick={() => setStep(3)}>Siguiente</button>
    </div>
    <img src={tabla} alt="Tabla de medidas" style={{ width: "100%", marginTop: 20 }} />

    
  </div>
)}

      {/* Paso 3 */}
      {step === 3 && (
        <div>
          <h2>Datos personales</h2>
          {["nombre", "cedula", "ciudad", "direccion", "barrio", "celular", "correo"].map((field) => (
  <input
    key={field}
    placeholder={field.charAt(0).toUpperCase() + field.slice(1)}
    onChange={(e) => handleDatosChange(field, e.target.value)}
    value={datos[field]}
    style={{ display: "block", margin: "10px 0", width: "100%", padding: 8 }}
    {...(field === "nombre" || field === "celular" ? { required: true } : {})}
    {...(field === "celular" ? { pattern: "\\d{10}" } : {})}
  />
))}
          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 20 }}>
            <button onClick={() => setStep(2)}>Atrás</button>
            <button onClick={handleSubmit}>Confirmar pedido</button>
          </div>
        </div>
      )}

      {/* Paso 4 */}
      {step === 4 && (
        <div style={{ textAlign: "center", marginTop: 60 }}>
          <h2>¡Gracias por tu pedido!</h2>
          <p>Te contactaremos pronto por WhatsApp.</p>
        </div>
      )}

      {/* Modal imagen ampliada */}
      {imagenAmpliada && (
        <div
          onClick={() => setImagenAmpliada(null)}
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            backgroundColor: "rgba(0,0,0,0.8)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            zIndex: 9999,
            cursor: "pointer"
          }}
        >
          <img
            src={imagenAmpliada}
            alt="Camisa ampliada"
            style={{ maxWidth: "90%", maxHeight: "90%", borderRadius: 10 }}
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </div>
  );
}
