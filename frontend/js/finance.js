// Personal finance management, income/expense tracking, budget views
async function loadExpenses() {
    try {
        const expenses = await apiFetch("/finance/expenses");
        const list = expenses.slice().reverse()
            .map(e => `<div class="expense-row"><span>${e.category}</span><span>₹${e.amount}</span><span>${e.date}</span></div>`)
            .join("");
        document.getElementById("expense-list").innerHTML = list || "No expenses yet.";
    } catch (err) {
        document.getElementById("expense-list").textContent = "Please log in to view your expenses.";
    }
}

document.getElementById("expense-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const category = document.getElementById("category").value;
    const amount = parseFloat(document.getElementById("amount").value);
    const date = document.getElementById("date").value;

    try {
        await apiFetch("/finance/expenses", {
            method: "POST",
            body: JSON.stringify({ category, amount, date }),
        });
        document.getElementById("expense-form").reset();
        loadExpenses();
    } catch (err) {
        alert("Failed to add expense: " + err.message);
    }
});

loadExpenses();