document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form");
    const lcdReadout = document.getElementById("lcdReadout");
    const lcdSub = document.getElementById("lcdSub");
    
    // Elementos del resumen del día
    const bdTotalHoras = document.getElementById("bdTotalHoras");
    const bdTemporada = document.getElementById("bdTemporada");
    const bdTipoDia = document.getElementById("bdTipoDia");
    const bdEquivalente = document.getElementById("bdEquivalente");

    form.addEventListener("submit", async (e) => {
        e.preventDefault(); 

        const formData = new FormData(form);
        lcdReadout.textContent = "Calculando...";
        if (lcdSub) lcdSub.textContent = "Procesando predicción...";

        try {
            const response = await fetch("/predict", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                // 1. Mostrar el consumo estimado en el medidor LCD
                lcdReadout.textContent = Number(data.prediction).toFixed(2);
                if (lcdSub) lcdSub.textContent = "Predicción calculada con éxito";
                
                // --- ESTO HACE QUE EL CUADRO LCD SE ACTIVE Y MUESTRE EL NÚMERO ---
                const lcdPanel = document.getElementById("lcdPanel");
                if (lcdPanel) {
                    lcdPanel.classList.remove("idle");
                    lcdPanel.classList.add("active");
                }
                
                // 2. Llenar el Resumen del día
                if (bdTotalHoras) bdTotalHoras.textContent = data.total_horas + " h";
                if (bdTemporada) bdTemporada.textContent = data.temporada;
                if (bdTipoDia) bdTipoDia.textContent = data.tipo_dia;
                
                if (bdEquivalente) {
                    const equivFocos = Math.round(data.prediction / 10);
                    bdEquivalente.textContent = `~${equivFocos} focos LED (10W)`;
                }
            } else {
                lcdReadout.textContent = "Error";
                if (lcdSub) lcdSub.textContent = data.error;
                console.error(data.error);
            }
        } catch (error) {
            lcdReadout.textContent = "Error";
            if (lcdSub) lcdSub.textContent = "Ocurrió un error de conexión.";
            console.error(error);
        }
    });
});