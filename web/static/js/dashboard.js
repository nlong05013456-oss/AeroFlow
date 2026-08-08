// DASHBOARD.JS
// Quản lý việc kết nối API backend, cập nhật chỉ số KPI, phân quyền đăng nhập và hiển thị biểu đồ Chart.js

document.addEventListener("DOMContentLoaded", () => {
    // --- KHAI BÁO CÁC ĐỐI TƯỢNG CHARTS ---
    let trendChart = null;
    let breakdownChart = null;
    let weatherChart = null;

    // --- CÁC PHẦN TỬ UI ---
    const carrierSelect = document.getElementById("carrier-select");
    const airportSelect = document.getElementById("airport-select");
    const monthSelect = document.getElementById("month-select");
    const holidayToggle = document.getElementById("holiday-toggle");
    const applyBtn = document.getElementById("apply-filters-btn");
    
    const kpiTotalFlights = document.getElementById("kpi-total-flights");
    const kpiTotalCancelled = document.getElementById("kpi-total-cancelled");
    const kpiTotalDelayed = document.getElementById("kpi-total-delayed");
    const kpiDelayRate = document.getElementById("kpi-delay-rate");
    const kpiAvgDelay = document.getElementById("kpi-avg-delay");

    const statusText = document.getElementById("status-text");
    const statusPulse = document.getElementById("status-pulse");
    const roleBadge = document.getElementById("role-badge");

    // Phân quyền & Modals
    const loginNavItem = document.getElementById("login-nav-item");
    const loginBtnText = document.getElementById("login-btn-text");
    const loginNavIcon = document.getElementById("login-nav-icon");
    const loginModal = document.getElementById("login-modal");
    const closeBtn = document.getElementById("close-modal-btn");
    const cancelBtn = document.getElementById("cancel-login-btn");
    const submitBtn = document.getElementById("submit-login-btn");
    const usernameInput = document.getElementById("username-input");
    const passwordInput = document.getElementById("password-input");
    const loginErrorMsg = document.getElementById("login-error-msg");
    const detailedSection = document.getElementById("detailed-tracker-section");
    const detailedTableBody = document.getElementById("detailed-table-body");

    let isTrackerLoggedIn = false;

    // --- 1. LẤY TRẠNG THÁI NGƯỜI DÙNG KHI MỞ TRANG ---
    function checkUserStatus() {
        fetch("/api/user-status")
            .then(res => res.json())
            .then(data => {
                if (data.logged_in) {
                    setTrackerLoggedInState();
                } else {
                    setGuestState();
                }
                loadFilters();
            })
            .catch(() => {
                setGuestState();
                loadFilters();
            });
    }

    function setTrackerLoggedInState() {
        isTrackerLoggedIn = true;
        loginBtnText.textContent = "Đăng xuất";
        loginNavIcon.className = "fa-solid fa-lock-open text-green";
        roleBadge.textContent = "FLIGHT TRACKER";
        roleBadge.style.background = "linear-gradient(135deg, var(--accent-purple), var(--accent-green))";
        detailedSection.classList.remove("hidden");
    }

    function setGuestState() {
        isTrackerLoggedIn = false;
        loginBtnText.textContent = "Đăng nhập";
        loginNavIcon.className = "fa-solid fa-lock";
        roleBadge.textContent = "PUBLIC USER";
        roleBadge.style.background = "linear-gradient(135deg, var(--accent-blue), var(--accent-purple))";
        detailedSection.classList.add("hidden");
        detailedTableBody.innerHTML = "";
    }

    // --- 2. LẤY DANH SÁCH BỘ LỌC TỪ API ---
    function loadFilters() {
        fetch("/api/filters")
            .then(res => res.json())
            .then(data => {
                updateStatusIndicator(data.mode);

                // Reset options nhưng giữ lại ALL
                carrierSelect.innerHTML = '<option value="ALL">Tất cả các hãng (ALL)</option>';
                airportSelect.innerHTML = '<option value="ALL">Tất cả sân bay (ALL)</option>';

                // Populate Hãng bay
                if (data.carriers) {
                    data.carriers.forEach(c => {
                        const opt = document.createElement("option");
                        opt.value = c.id;
                        opt.textContent = `${c.id} - ${c.name}`;
                        carrierSelect.appendChild(opt);
                    });
                }

                // Populate Sân bay
                if (data.airports) {
                    data.airports.forEach(ap => {
                        const opt = document.createElement("option");
                        opt.value = ap;
                        opt.textContent = ap;
                        airportSelect.appendChild(opt);
                    });
                }

                refreshDashboard();
            })
            .catch(err => {
                console.error("Lỗi khi load filters:", err);
                updateStatusIndicator("RED");
                refreshDashboard();
            });
    }

    // --- 3. CẬP NHẬT TRẠNG THÁI KẾT NỐI GCP ---
    function updateStatusIndicator(mode) {
        statusPulse.className = "pulse-indicator";
        
        if (mode === "CLOUD") {
            statusText.textContent = "GCP Cloud (BigQuery)";
            statusPulse.classList.add("green");
        } else if (mode === "MOCK") {
            statusText.textContent = "Giả lập (Mock Mode)";
            statusPulse.classList.add("orange");
        } else {
            statusText.textContent = "Lỗi kết nối";
            statusPulse.classList.add("red");
        }
    }

    // --- 4. LÀM MỚI TOÀN BỘ CHỈ SỐ VÀ BIỂU ĐỒ ---
    function refreshDashboard() {
        applyBtn.disabled = true;
        applyBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang tải...';

        const carrier = carrierSelect.value;
        const airport = airportSelect.value;
        const month = monthSelect.value;
        const isHoliday = holidayToggle.checked;

        const url = `/api/analytics?carrier=${carrier}&airport=${airport}&month=${month}&is_holiday=${isHoliday}`;

        fetch(url)
            .then(res => res.json())
            .then(data => {
                applyBtn.disabled = false;
                applyBtn.innerHTML = '<i class="fa-solid fa-sync"></i> Áp dụng';

                if (data.error) {
                    console.error("API Error:", data.error);
                    alert("Lỗi truy vấn dữ liệu BigQuery: " + data.error);
                    return;
                }

                updateStatusIndicator(data.mode);

                // Cập nhật KPIs
                kpiTotalFlights.textContent = data.kpis.total_flights.toLocaleString();
                kpiTotalCancelled.textContent = data.kpis.total_cancelled.toLocaleString();
                kpiTotalDelayed.textContent = data.kpis.total_delayed.toLocaleString();
                kpiDelayRate.textContent = `${data.kpis.delay_rate}%`;
                kpiAvgDelay.textContent = `${data.kpis.avg_delay_minutes} m`;

                // Cập nhật Biểu đồ
                renderTrendChart(data.monthly_trend);
                renderBreakdownChart(data.delay_breakdown);
                renderWeatherChart(data.weather_impact);

                // Cập nhật bảng dữ liệu chi tiết nếu vai trò là Tracker
                if (data.role === "tracker" && data.details_table) {
                    detailedSection.classList.remove("hidden");
                    renderDetailsTable(data.details_table);
                } else {
                    detailedSection.classList.add("hidden");
                }
            })
            .catch(err => {
                applyBtn.disabled = false;
                applyBtn.innerHTML = '<i class="fa-solid fa-sync"></i> Áp dụng';
                console.error("Lỗi khi tải dữ liệu phân tích:", err);
            });
    }

    // --- 5. VẼ BẢNG GIÁM SÁT CHI TIẾT ---
    function renderDetailsTable(rows) {
        detailedTableBody.innerHTML = "";
        
        if (rows.length === 0) {
            const tr = document.createElement("tr");
            tr.innerHTML = '<td colspan="9" style="text-align: center; color: var(--text-secondary);">Không tìm thấy chuyến bay chi tiết nào phù hợp bộ lọc.</td>';
            detailedTableBody.appendChild(tr);
            return;
        }

        rows.forEach(r => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${r.date_key}</td>
                <td><strong>${r.carrier_name}</strong></td>
                <td>#${r.flight_number}</td>
                <td><span class="badge" style="background: rgba(0, 180, 216, 0.15); color: var(--accent-blue);">${r.origin_airport_key}</span></td>
                <td><span class="badge" style="background: rgba(114, 9, 183, 0.15); color: var(--accent-purple);">${r.dest_airport_key}</span></td>
                <td style="font-family: monospace; font-size: 11px; color: var(--text-secondary);">${r.masked_tail_number}</td>
                <td class="${r.dep_delay > 0 ? 'text-red' : 'text-green'}">${r.dep_delay > 0 ? '+' + r.dep_delay : r.dep_delay} m</td>
                <td class="${r.arr_delay > 0 ? 'text-red' : 'text-green'}">${r.arr_delay > 0 ? '+' + r.arr_delay : r.arr_delay} m</td>
                <td>${r.elevation_ft.toLocaleString()} ft</td>
            `;
            detailedTableBody.appendChild(tr);
        });
    }

    // --- 6. VẼ BIỂU ĐỒ XU HƯỚNG THEO THÁNG ---
    function renderTrendChart(trendData) {
        const ctx = document.getElementById("trendChart").getContext("2d");
        
        if (trendChart) {
            trendChart.destroy();
        }

        trendChart = new Chart(ctx, {
            type: "bar",
            data: {
                labels: trendData.labels,
                datasets: [
                    {
                        label: "Tổng Chuyến Bay",
                        data: trendData.flights,
                        backgroundColor: "rgba(0, 180, 216, 0.4)",
                        borderColor: "rgba(0, 180, 216, 1)",
                        borderWidth: 1,
                        yAxisID: "y"
                    },
                    {
                        label: "Số Chuyến Trễ",
                        data: trendData.delays,
                        type: "line",
                        borderColor: "rgba(247, 127, 0, 1)",
                        backgroundColor: "rgba(247, 127, 0, 0.2)",
                        borderWidth: 2,
                        tension: 0.3,
                        fill: false,
                        yAxisID: "y"
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: "#9aa0a6", font: { family: "Outfit" } }
                    }
                },
                scales: {
                    x: {
                        grid: { color: "rgba(255, 255, 255, 0.05)" },
                        ticks: { color: "#9aa0a6", font: { family: "Outfit" } }
                    },
                    y: {
                        grid: { color: "rgba(255, 255, 255, 0.05)" },
                        ticks: { color: "#9aa0a6", font: { family: "Outfit" } }
                    }
                }
            }
        });
    }

    // --- 7. VẼ BIỂU ĐỒ PHÂN BỔ NGUYÊN NHÂN TRỄ ---
    function renderBreakdownChart(breakdownData) {
        const ctx = document.getElementById("breakdownChart").getContext("2d");

        if (breakdownChart) {
            breakdownChart.destroy();
        }

        breakdownChart = new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: ["Do Hãng bay", "Do Thời tiết", "Hệ thống NAS", "Bảo mật", "Máy bay trễ"],
                datasets: [{
                    data: [
                        breakdownData.carrier,
                        breakdownData.weather,
                        breakdownData.nas,
                        breakdownData.security,
                        breakdownData.late_aircraft
                    ],
                    backgroundColor: [
                        "#00b4d8", // Blue
                        "#ffd166", // Yellow
                        "#ef476f", // Red
                        "#06d6a0", // Green
                        "#7209b7"  // Purple
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { color: "#9aa0a6", font: { family: "Outfit" } }
                    }
                }
            }
        });
    }

    // --- 8. VẼ BIỂU ĐỒ THỜI TIẾT ---
    function renderWeatherChart(weatherData) {
        const ctx = document.getElementById("weatherChart").getContext("2d");

        if (weatherChart) {
            weatherChart.destroy();
        }

        weatherChart = new Chart(ctx, {
            type: "bar",
            data: {
                labels: weatherData.labels,
                datasets: [{
                    label: "Tỷ lệ trễ cất cánh (%)",
                    data: weatherData.delay_rates,
                    backgroundColor: [
                        "rgba(6, 214, 160, 0.5)",
                        "rgba(255, 209, 102, 0.5)",
                        "rgba(239, 71, 111, 0.5)"
                    ],
                    borderColor: [
                        "#06d6a0",
                        "#ffd166",
                        "#ef476f"
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        grid: { color: "rgba(255, 255, 255, 0.05)" },
                        ticks: { color: "#9aa0a6", font: { family: "Outfit" } },
                        max: 100
                    },
                    y: {
                        grid: { display: false },
                        ticks: { color: "#9aa0a6", font: { family: "Outfit" } }
                    }
                }
            }
        });
    }

    // --- 9. XỬ LÝ ĐĂNG NHẬP / ĐĂNG XUẤT ---
    loginNavItem.addEventListener("click", (e) => {
        e.preventDefault();
        
        if (isTrackerLoggedIn) {
            // Đăng xuất
            fetch("/api/logout", { method: "POST" })
                .then(res => res.json())
                .then(data => {
                    setGuestState();
                    refreshDashboard();
                    alert(data.message);
                });
        } else {
            // Mở Modal đăng nhập
            loginModal.classList.add("active");
            loginErrorMsg.style.display = "none";
            usernameInput.value = "";
            passwordInput.value = "";
        }
    });

    // Đóng Modal
    function closeModal() {
        loginModal.classList.remove("active");
    }
    closeBtn.addEventListener("click", closeModal);
    cancelBtn.addEventListener("click", closeModal);

    // Xác nhận đăng nhập
    submitBtn.addEventListener("click", () => {
        const username = usernameInput.value;
        const password = passwordInput.value;

        fetch("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        })
        .then(res => {
            if (!res.ok) {
                throw new Error("Invalid login");
            }
            return res.json();
        })
        .then(data => {
            closeModal();
            setTrackerLoggedInState();
            refreshDashboard();
            alert(data.message);
        })
        .catch(() => {
            loginErrorMsg.style.display = "block";
        });
    });

    // --- SỰ KIỆN CLICK ÁP DỤNG BỘ LỌC ---
    applyBtn.addEventListener("click", refreshDashboard);

    // --- KHỞI ĐỘNG HỆ THỐNG ---
    checkUserStatus();
});
