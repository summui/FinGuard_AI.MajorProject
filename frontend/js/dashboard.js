// Dashboard summary views and recent activity loading
async function loadDashboard() {
    try {
        const profile = await apiFetch("/finance/profile");
        const expenses = await apiFetch("/finance/expenses");

        const totalExpenses = expenses.reduce((sum, e) => sum + e.amount, 0);
        const savings = (profile.monthly_salary || 0) - totalExpenses - (profile.total_emi || 0);

        document.getElementById("metric-salary").textContent = `₹${(profile.monthly_salary || 0).toLocaleString()}`;
        document.getElementById("metric-expenses").textContent = `₹${totalExpenses.toLocaleString()}`;
        document.getElementById("metric-savings").textContent = `₹${savings.toLocaleString()}`;

        const recentList = expenses.slice(-5).reverse()
            .map(e => `<div class="expense-row"><span>${e.category}</span><span>₹${e.amount}</span><span>${e.date}</span></div>`)
            .join("");
        document.getElementById("recent-expenses").innerHTML = recentList || "No expenses yet.";
    } catch (err) {
        document.getElementById("recent-expenses").textContent = "Please log in to view your dashboard.";
    }
}

loadDashboard();