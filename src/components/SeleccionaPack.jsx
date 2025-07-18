// components/SeleccionaPack.jsx
import React from "react";

const packs = [
  {
    cantidad: "1 Camisa",
    numero: 1,
    precio: "$115.000",
    envio: "🚚 Envío gratis",
    bg: "bg-white",
    destaque: false,
    tachado: false,
  },
  {
    cantidad: "🔥 Pack de 3 Camisas",
    numero: 3,
    precioAnterior: "$345.000",
    precio: "$295.000",
    envio: "🚚 ¡Envío gratis!",
    bg: "bg-blue-600 text-white",
    destaque: true,
    tachado: true,
  },
  {
    cantidad: "Pack de 6 Camisas",
    numero: 6,
    precioAnterior: "$690.000",
    precio: "$495.000",
    envio: "🚚 ¡Envío gratis!",
    bg: "bg-yellow-400",
    destaque: false,
    tachado: true,
  },
];

const SeleccionaPack = ({ onPackSelect }) => {
  const handleClick = (cantidad) => {
  if (onPackSelect) {
    onPackSelect(cantidad);

    // Esperamos a que React termine de renderizar el paso 2
    setTimeout(() => {
      const paso2 = document.getElementById("paso2");
      if (paso2) {
        const offset = -80; // Ajusta si tienes un header fijo
        const top = paso2.getBoundingClientRect().top + window.pageYOffset + offset;

        window.scrollTo({ top, behavior: "smooth" });
      }
    }, 300); // Tiempo suficiente para que el DOM cargue el nuevo paso
  }
};



  return (
    <section className="py-20 px-4 bg-gray-100" id="packs">
      <div className="max-w-6xl mx-auto text-center">
        <h2 className="text-4xl font-extrabold text-gray-800 mb-12">
          🔥 ¡Elige tu pack y aprovecha la oferta!
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-10">
          {packs.map((pack, index) => (
            <div
              key={index}
              className={`relative rounded-2xl shadow-2xl p-8 transition-all duration-300 transform hover:scale-105 cursor-pointer ${pack.bg} ${
                pack.destaque ? "ring-4 ring-blue-800" : ""
              }`}
              onClick={() => handleClick(pack.numero)}
            >
              <h3 className="text-2xl font-bold mb-3">{pack.cantidad}</h3>

              <div className="relative w-fit mx-auto mb-2">
                <p className={`text-lg ${pack.destaque ? "text-gray-200" : "text-gray-500"}`}>
                  {pack.precioAnterior}
                </p>
                {pack.tachado && (
                  <div
                    className="absolute left-0 top-1/2 w-full h-0.5 bg-red-600 origin-left scale-x-0 animate-diagonal-line"
                    style={{ transform: "rotate(12deg)" }}
                  ></div>
                )}
              </div>

              <p className="text-4xl font-extrabold mb-4">{pack.precio}</p>
              <p className={`mb-6 font-medium ${pack.destaque ? "text-white" : "text-green-700"}`}>
                {pack.envio}
              </p>
              <button
                className={`w-full py-3 text-lg font-bold rounded-xl transition duration-300 animate-boton-bounce ${
                  pack.destaque
                    ? "bg-white text-blue-700 hover:bg-gray-100"
                    : "bg-black text-white hover:bg-gray-800"
                } shadow-lg hover:shadow-xl`}
              >
                ¡Lo quiero ahora!
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default SeleccionaPack;
