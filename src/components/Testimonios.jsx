import React from "react";

const testimonios = [
  {
    nombre: "David M.",
    texto: "Estoy muy satisfecho con mi compra. Excelente diseño y acabado. Se nota la calidad desde que te la pones.",
  },
  {
    nombre: "Daniel G.",
    texto: "Muy cómoda y elegante, ideal tanto para el trabajo como para salir. ¡Ya quiero comprar más colores!",
  },
  {
    nombre: "Carlos R.",
    texto: "La tela es premium de verdad. Pedí una y terminé comprando tres más. ¡Recomendadas al 100%!",
  },
  {
    nombre: "Valentina H.",
    texto: "La atención fue excelente y el envío muy rápido. Las camisas llegaron impecables y con buena presentación.",
  },
  {
    nombre: "Andrés L.",
    texto: "Me sorprendió la calidad. Ajuste perfecto, buenos acabados y el estilo es justo lo que buscaba.",
  },
];

const Testimonios = () => {
  return (
    <section className="bg-white py-16 px-4" id="testimonios">
      <div className="max-w-6xl mx-auto text-center">
        <h2 className="text-3xl md:text-4xl font-bold mb-12 text-gray-900">Lo que opinan nuestros clientes</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {testimonios.map((item, index) => (
            <div
              key={index}
              className="bg-white border border-gray-200 shadow-lg rounded-2xl p-6 transition-all duration-300 hover:scale-105 hover:shadow-2xl"
            >
              <div className="text-xl font-semibold text-gray-800 mb-2">{item.nombre}</div>
              <div className="text-yellow-500 text-lg mb-2">★★★★★</div>
              <p className="text-gray-600 italic">“{item.texto}”</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Testimonios;
