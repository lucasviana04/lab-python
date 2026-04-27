const API_URL = "http://127.0.0.1:8000";

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

document.getElementById("ingredient-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("name").value;
    const category = document.getElementById("category").value;
    
    // Gera a data de hoje no formato YYYY-MM-DD que o seu banco pede
    const today = new Date().toISOString().split('T')[0];

    try {
        // 1. Tenta criar o ingrediente
        let ingRes = await fetch(`${API_URL}/ingredients/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, category })
        });

        let ingredient;
        if (ingRes.status === 400 || ingRes.status === 422) {
            // Se já existe ou deu erro de validação, buscamos o ID na lista existente
            const allIng = await fetch(`${API_URL}/ingredients/`);
            const data = await allIng.json();
            ingredient = data.find(i => i.name.toLowerCase() === name.toLowerCase());
        } else {
            ingredient = await ingRes.json();
        }

        // 2. Adiciona à despensa com a DATA obrigatória
        if (ingredient && ingredient.id) {
            const pantryRes = await fetch(`${API_URL}/pantry/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ 
                    ingredient_id: ingredient.id, 
                    quantity: "1 unit",
                    expiry_date: today // O CAMPO QUE FALTAVA!
                })
            });

            if (pantryRes.ok) {
                document.getElementById("ingredient-form").reset();
                fetchPantry();
            } else {
                const err = await pantryRes.json();
                console.error("Pantry Error:", err);
                alert("Erro ao salvar na despensa. Verifique o console.");
            }
        }
    } catch (error) {
        console.error("System Error:", error);
    }
});

// IA: Gerar Receita
document.getElementById("get-recipe-btn").addEventListener("click", async () => {
    const display = document.getElementById("recipe-display");
    display.innerText = "Gemini is thinking... 🍳";
    
    try {
        const response = await fetch(`${API_URL}/ai/suggest-recipe`);
        const data = await response.json();
        if (response.ok) {
            display.innerText = data.suggestion;
        } else {
            display.innerText = "Add items to your pantry first!";
        }
    } catch (error) {
        display.innerText = "AI Service unavailable.";
    }
});

async function deleteItem(id) {
    if (confirm("Remove?")) {
        await fetch(`${API_URL}/pantry/${id}`, { method: "DELETE" });
        fetchPantry();
    }
}