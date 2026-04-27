const API_URL = "http://127.0.0.1:8000";

// 1. Carregar a despensa ao abrir a página
document.addEventListener("DOMContentLoaded", fetchPantry);

async function fetchPantry() {
    const list = document.getElementById("pantry-items");
    try {
        const response = await fetch(`${API_URL}/pantry/`);
        const items = await response.json();
        list.innerHTML = "";
        items.forEach(item => {
            const li = document.createElement("li");
            li.innerHTML = `
                <span><strong>${item.ingredient.name}</strong> - Valid: ${item.expiry_date}</span>
                <button onclick="deleteItem(${item.id})" style="background: #ef4444; border-radius: 4px; padding: 5px 10px; color: white; border: none; cursor: pointer;">Delete</button>
            `;
            list.appendChild(li);
        });
    } catch (error) {
        console.error("Error fetching pantry:", error);
    }
}

// 2. Adicionar ingrediente
document.getElementById("ingredient-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("name").value;
    const category = document.getElementById("category").value;
    const today = new Date().toISOString().split('T')[0];

    try {
        let ingRes = await fetch(`${API_URL}/ingredients/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, category })
        });

        let ingredient;
        if (ingRes.status === 400 || ingRes.status === 422) {
            const allIng = await fetch(`${API_URL}/ingredients/`);
            const data = await allIng.json();
            ingredient = data.find(i => i.name.toLowerCase() === name.toLowerCase());
        } else {
            ingredient = await ingRes.json();
        }

        if (ingredient && ingredient.id) {
            await fetch(`${API_URL}/pantry/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ 
                    ingredient_id: ingredient.id, 
                    quantity: "1 unit",
                    expiry_date: today
                })
            });
            document.getElementById("ingredient-form").reset();
            fetchPantry();
        }
    } catch (error) {
        console.error("Error adding item:", error);
    }
});

// 3. GERAR RECEITA (O botão que estava mudo)
document.getElementById("get-recipe-btn").addEventListener("click", async () => {
    // Alerta de teste para confirmar que o JS está vivo
    console.log("Botão clicado!");
    
    const display = document.getElementById("recipe-display");
    display.innerText = "Gemini is cooking up an idea... 🍳";
    
    try {
        const response = await fetch(`${API_URL}/ai/suggest-recipe`);
        const data = await response.json();
        
        if (response.ok) {
            display.innerText = data.suggestion;
        } else {
            display.innerText = "Error: " + (data.detail || "Check your pantry.");
        }
    } catch (error) {
        console.error("AI Error:", error);
        display.innerText = "AI Service unavailable. Check if Backend is running.";
    }
});

// 4. Deletar item
async function deleteItem(id) {
    if (confirm("Remove this item?")) {
        await fetch(`${API_URL}/pantry/${id}`, { method: "DELETE" });
        fetchPantry();
    }
}