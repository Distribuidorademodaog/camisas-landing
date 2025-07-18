import { useState, useEffect } from 'react';
import emailjs from '@emailjs/browser';

import modelo from './assets/camisas.jpg';
import modelo2 from './assets/camisa2.jpg';
import tabla from './assets/tabla.jpg';
import uno from './assets/1camisa.png';
import tres from './assets/3camisas.png';
import seis from './assets/6camisas.png';
import oferta from './assets/oferta.png';
import camisas2 from "./assets/camisas2.jpg";
import Testimonios from "./components/Testimonios";
import SeleccionaPack from "./components/SeleccionaPack";
import './index.css';




// Colores
import amarillo from './assets/camisas/camisa-amarillo.jpg';
import rojo from './assets/camisas/camisa-rojo.jpg';
import azulmedio from './assets/camisas/camisa-azulmedio.jpg';
import blanco from './assets/camisas/camisa-blanco.jpg';
import verdeoscuro from './assets/camisas/camisa-verdeoscuro.jpg';
import verdeclaro from './assets/camisas/camisa-verdeclaro.jpg';
import negro from './assets/camisas/camisa-negro.jpg';
import rosada from './assets/camisas/camisa-rosada.jpg';
import bossazul from './assets/camisas/boss-azul.jpg';
import rayasamarillo from './assets/camisas/rayas-amarilla.jpg';

import linoazulclaro from './assets/camisas/tipolino-azulclaro.jpg';
import linoazuloscuro from './assets/camisas/tipolino-azuloscuro.jpg';
import linoverdeclaro from './assets/camisas/tipolino-verdeclaro.jpg';
import linoverdemilitar from './assets/camisas/tipolino-verdemilitar.jpg';
import linoblanco from './assets/camisas/tipolino-blanco.jpg';
import linoterracota from './assets/camisas/tipolino-terracota.jpg';
import linonegro from './assets/camisas/tipolino-negro.jpg';
import linobeige from './assets/camisas/tipolino-beige.jpg';
import CHazul from './assets/camisas/cuadrosch-azul.jpg';
import CHnegro from './assets/camisas/cuadrosch-negro.jpg';
import CHrojo from './assets/camisas/cuadrosch-rojo.jpg';
import CHverde from './assets/camisas/cuadrosch-verde.jpg';
import videoCamisas from './assets/video-camisas.mp4';
import videoCamisas1 from './assets/videocamisas1.mp4';
import { preloadModule } from 'react-dom';



const tallas = ["S", "M", "L", "XL", "XXL", "3XL"];

const colores = [
  { nombre: "Negro", img: negro, tallas: ["S", "M", "L", "XL", "XXL", "3XL"] },
  { nombre: "Blanco", img: blanco, tallas: ["S", "M", "L", "XL", "XXL", "3XL"] },
  { nombre: "rojo", img: rojo, tallas: ["S", "M", "L", "XL", "XXL", "3XL"] },
  { nombre: "rosada", img: rosada, tallas: ["S", "M", "L", "XL", "XXL"] },
  { nombre: "Amarillo", img: amarillo, tallas: ["S", "M", "L", "XL", "XXL", "3XL"] },
  { nombre: "verde oscuro", img: verdeoscuro, tallas: [ "M", "L", "3XL"] },
  { nombre: "verde claro", img: verdeclaro, tallas: ["S", "M", "L", "XL", "XXL", "3XL"] },
  { nombre: "Boss azul", img: bossazul, tallas: ["S", "M", "L", "XL"] },
  { nombre: "rayas amarillo", img: rayasamarillo, tallas: ["S", "M", "L", "XL", "3XL"] },

  { nombre: "Tipo lino 100% alg azul claro", img: linoazulclaro, tallas: ["M", "L", "XL", "XXL", "3XL"] },
  { nombre: "Tipo lino 100% alg azul oscuro", img: linoazuloscuro, tallas: ["S", "M", "L", "XL", "XXL", "3XL"] },
  { nombre: "Tipo lino 100% alg verde claro", img: linoverdeclaro, tallas: ["S", "M", "L", "XL", "XXL", "3XL"] },
  { nombre: "Tipo lino 100% alg verde militar", img: linoverdemilitar, tallas: ["S", "M", "L", "XXL", "3XL"] },
  { nombre: "Tipo lino 100% alg terracota", img: linoterracota, tallas: [ "M", "L", "XL", "XXL", "3XL"] },
  { nombre: "Tipo lino 100% alg negro", img: linonegro, tallas: ["S", "M", "L", "XL", "XXL", "3XL"] },
  { nombre: "Tipo lino 100% alg beige", img: linobeige, tallas: ["S", "M", "L", "XXL", "3XL"] },
  
  
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
  fetch("https://n8n.paquetecompleto.com.co/webhook/nuevo-pedido", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      name: datos.nombre,
      phone: "+57" + datos.celular,
      email: datos.correo,
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
      <div className="bg-green-500 text-white p-4 rounded-lg text-center mb-4">

</div>

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

          {/* ─── Dos videos lado a lado ─────────────────────────────── */}
<div
  style={{
    display: "flex",
    flexWrap: "wrap",     // se apilan en móvil
    gap: 20,
    justifyContent: "center",
    margin: "30px 0",
  }}
>
  {/* Video original */}
  <video
    src={videoCamisas}
    controls
    autoPlay
    muted
    loop
    playsInline
    style={{
      width: "100%",
      maxWidth: 400,
      borderRadius: 10,
      objectFit: "cover",
    }}
  />

  {/* Segundo video, mismo tamaño */}
  <video
    src={videoCamisas1}
    controls
    autoPlay
    muted
    loop
    playsInline
    style={{
      width: "100%",
      maxWidth: 400,
      borderRadius: 10,
      objectFit: "cover",
    }}
  />
</div>


          <div style={{ backgroundColor: "#001f3f", padding: 12, borderRadius: 6, margin: "20px 0", color: "#fff", textAlign: "center" }}>
            <h2 style={{ margin: 0 }}>Selecciona un pack</h2>
          </div>

          {/* Selección de packs con Tailwind */}
<div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mt-6">
  {[{ cant: 1, precio: 115000, anterior: 115000 }, { cant: 3, precio: 295000, anterior: 345000 }, { cant: 6, precio: 495000, anterior: 690000 }].map((pack, index) => (
    <div key={index} className="bg-white rounded-lg shadow-md p-4 text-center border hover:border-gray-800 transition-all">
      <h3 className="text-xl font-semibold mb-2">{pack.cant} Camisa{pack.cant > 1 && 's'}</h3>
      <p className="line-through text-gray-500 text-sm">${pack.anterior.toLocaleString()}</p>
      <p className="text-2xl font-bold text-green-600 mb-2">${pack.precio.toLocaleString()}</p>
      <p className="text-sm mb-2">{pack.cant > 1 ? '🚚 ¡Envío gratis!' : '🚚 Envío gratis'}</p>
      <button
        className="bg-black text-white px-4 py-2 rounded hover:bg-gray-800"
        onClick={() => handlePackSelect(pack.cant)}
      >
        ¡Lo quiero ahora!
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
      <Testimonios />
<SeleccionaPack onPackSelect={handlePackSelect} />


        </>
      )}




{/* ---------------- PASO 2 ---------------- */}
{step === 2 && (
    <section id="paso2" className="py-20">
    {/* Miniaturas de referencia */}
    <div style={{ marginTop: 30 }}>
      <h3 style={{ marginBottom: 10 }}>Colores disponibles:</h3>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(90px, 1fr))",
          gap: 15,
          justifyItems: "center",
        }}
      >
        {colores.map((c, idx) => (
          <div key={idx} style={{ textAlign: "center" }}>
            <img
              src={c.img}
              alt={c.nombre}
              style={{
                width: 60,
                height: 60,
                objectFit: "cover",
                borderRadius: 6,
                border: "1px solid #ccc",
                cursor: "pointer",
              }}
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
      const imgColor = obtenerImagenColor(camisa.color);
      return (
        <div key={i} style={{ marginBottom: 30 }}>
          <p>Camisa {i + 1}</p>

          <select onChange={e => handleCamisaChange(i, "color", e.target.value)}>
            <option value="">Selecciona color</option>
            {colores.map((c, idx) => (
              <option key={c.nombre} value={c.nombre}>
                {idx + 1}. {c.nombre}
              </option>
            ))}
          </select>
  
{camisa.color && (
  <select
    onChange={e => handleCamisaChange(i, "talla", e.target.value)}
    style={{ marginLeft: 10 }}
    value={camisa.talla}
  >
    <option value="">Selecciona talla</option>
    {tallas.map(t => {
      const tallasDisponibles = colores.find(c => c.nombre === camisa.color)?.tallas || [];
      const disponible = tallasDisponibles.includes(t);
      return (
        <option
          key={t}
          value={t}
          disabled={!disponible}
          style={{ color: disponible ? "#000" : "#999", textDecoration: disponible ? "none" : "line-through" }}
        >
          {t}
        </option>
      );
    })}
  </select>
)}



          {/* Vista previa */}
          {camisa.color && imgColor && (
            <div style={{ marginTop: 10 }}>
              <img
                src={imgColor}
                alt={camisa.color}
                style={{
                  width: 80,
                  height: 80,
                  objectFit: "cover",
                  borderRadius: 6,
                  cursor: "pointer",
                }}
                onClick={() => setImagenAmpliada(imgColor)}
              />
              <p style={{ fontSize: 14 }}>{camisa.color}</p>
            </div>
          )}
        </div>
      );
    })}

    {/* Navegación */}
    <div style={{ display: "flex", justifyContent: "space-between", marginTop: 20 }}>
      <button onClick={() => setStep(1)}>Atrás</button>
      <button onClick={() => setStep(3)}>Siguiente</button>
    </div>

    <img src={tabla} alt="Tabla de medidas" style={{ width: "100%", marginTop: 20 }} />
   </section>

)} {/* ← cierre correcto del paso 2 */}

{/* ---------- Modal global con ❌ ---------- */}
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
      cursor: "pointer",
    }}
  >
    <button
      onClick={() => setImagenAmpliada(null)}
      style={{
        position: "absolute",
        top: 20,
        right: 20,
        background: "#fff",
        border: "none",
        fontSize: 24,
        fontWeight: "bold",
        borderRadius: "50%",
        width: 40,
        height: 40,
        lineHeight: "40px",
        textAlign: "center",
        cursor: "pointer",
        boxShadow: "0 0 10px rgba(0,0,0,0.4)",
      }}
    >
      ×
    </button>

    <img
      src={imagenAmpliada}
      alt="Camisa ampliada"
      style={{ maxWidth: "90%", maxHeight: "90%", borderRadius: 10 }}
      onClick={e => e.stopPropagation()}
    />
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
          <div className="mt-10 text-center">
  <h3 className="text-2xl font-bold mb-4">Visita nuestra página de Polos</h3>

  <a href="https://camisas-polos.vercel.app/" target="_blank" rel="noopener noreferrer">
    <img
      src={camisas2} // Asegúrate de importar esta imagen arriba como: import camisas2 from './assets/camisas2.jpg';
      alt="Polos"
      className="mx-auto rounded-xl shadow-xl w-full max-w-xl hover:scale-105 transition-transform duration-300 cursor-pointer"
    />
  </a>

  <a
    href="https://camisas-polos.vercel.app/"
    target="_blank"
    rel="noopener noreferrer"
    className="inline-block mt-6 px-6 py-3 text-white bg-blue-700 rounded-lg font-semibold hover:bg-blue-800 transition"
  >
    Visita página de Polos
  </a>
</div>

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