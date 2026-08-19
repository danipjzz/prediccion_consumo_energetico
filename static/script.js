document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form");
    
    // Crear dinámicamente un espacio sutil para mostrar el resultado si no existe
    let resultContainer = document.querySelector("#result-output");
    if (!resultContainer) {
        resultContainer = document.createElement("div");
        resultContainer.id = "result-output";
        resultContainer.style.cssText = `
            margin-top: 25px;
            text-align: center;
            font-family: 'Instrument Serif', serif;
            font-size: 28px;
            color: #332f2e;
            letter-spacing: 0.5px;
        `;
        form.parentNode.appendChild(resultContainer);
    }

    form.addEventListener("submit", async (e) => {
        e.preventDefault(); // Evita que la página se recargue

        // Recopilar los datos del formulario
        const formData = new FormData(form);
        
        resultContainer.textContent = "Calculando predicción...";

        try {
            const response = await fetch("/predict", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                // Mostrar el resultado con un formato limpio y elegante
                resultContainer.textContent = `Consumo estimado: ${data.prediction} Wh`;
            } else {
                resultContainer.textContent = "Error al calcular el consumo.";
                console.error(data.error);
            }
        } catch (error) {
            resultContainer.textContent = "Ocurrió un error de conexión.";
            console.error(error);
        }
    });
});