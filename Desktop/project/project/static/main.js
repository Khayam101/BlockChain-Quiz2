document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".reveal-secret").forEach((button) => {
        button.addEventListener("click", () => {
            const panel = button.closest(".secret-panel");
            const secret = panel.dataset.secret;
            const value = panel.querySelector(".masked-secret");
            const isRevealed = button.dataset.revealed === "true";

            value.textContent = isRevealed
                ? `${secret.slice(0, 6)}...${secret.slice(-6)}`
                : secret;
            button.textContent = isRevealed ? "Reveal" : "Mask";
            button.dataset.revealed = isRevealed ? "false" : "true";
        });
    });

    document.querySelectorAll(".glass-card").forEach((card) => {
        card.addEventListener("mousemove", (event) => {
            const rect = card.getBoundingClientRect();
            const x = ((event.clientX - rect.left) / rect.width) * 100;
            const y = ((event.clientY - rect.top) / rect.height) * 100;

            card.style.background = `
                radial-gradient(circle at ${x}% ${y}%, rgba(24, 255, 146, 0.13), transparent 34%),
                linear-gradient(180deg, rgba(255, 255, 255, 0.065), rgba(255, 255, 255, 0.025)),
                rgba(13, 18, 28, 0.72)
            `;
        });

        card.addEventListener("mouseleave", () => {
            card.style.background = "";
        });
    });
});
