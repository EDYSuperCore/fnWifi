document.addEventListener('DOMContentLoaded', function() {
    function fetchWifiList() {
        fetch('/wifi_list')
            .then(response => response.json())
            .then(data => {
                const wifiList = document.getElementById('wifi-list').getElementsByTagName('tbody')[0];
                wifiList.innerHTML = ''; // 清空现有内容
                const currentWifi = data.current_wifi;
                data.wifi_list.forEach(line => {
                    if (line.length === 3) {
                        const [ssid, security, signal] = line.map(decodeURIComponent); // 确保SSID, 安全性和信号强度正确解码
                        const row = wifiList.insertRow();
                        const ssidCell = row.insertCell(0);
                        const securityCell = row.insertCell(1);
                        const signalCell = row.insertCell(2);
                        const actionCell = row.insertCell(3);

                        ssidCell.textContent = ssid;
                        if (ssid === currentWifi) {
                            const tag = document.createElement('span');
                            tag.className = 'tag';
                            tag.textContent = '已连接';
                            ssidCell.appendChild(tag);

                            const disconnectButton = document.createElement('button');
                            disconnectButton.textContent = '断开';
                            disconnectButton.className = 'btn btn-disconnect';
                            disconnectButton.onclick = () => confirmDisconnect(ssid);
                            actionCell.appendChild(disconnectButton);
                        } else {
                            const connectButton = document.createElement('button');
                            connectButton.textContent = '连接';
                            connectButton.className = 'btn btn-connect';
                            connectButton.onclick = () => showDialog(ssid);
                            actionCell.appendChild(connectButton);
                        }
                        securityCell.textContent = security;

                        const signalBar = document.createElement('div');
                        signalBar.className = 'signal-bar';
                        signalBar.style.width = signal + '%';
                        signalCell.appendChild(signalBar);
                    }
                });
            })
            .catch(error => {
                console.error('获取 WiFi 列表时出错:', error);
                const wifiList = document.getElementById('wifi-list').getElementsByTagName('tbody')[0];
                wifiList.innerHTML = '<tr><td colspan="4">加载 WiFi 列表时出错</td></tr>';
            });
    }

    fetchWifiList();
    setInterval(fetchWifiList, 5000); // 每5秒刷新一次

    function showDialog(ssid) {
        const dialog = document.getElementById('wifi-dialog');
        dialog.style.display = 'flex';
        const connectBtn = document.getElementById('connect-btn');
        connectBtn.onclick = () => connectToWifi(ssid);

        // 监听输入框的回车键事件
        const passwordInput = document.getElementById('wifi-password');
        passwordInput.onkeydown = (event) => {
            if (event.key === 'Enter') {
                connectBtn.click();
            }
        };
    }

    function closeDialog() {
        const dialog = document.getElementById('wifi-dialog');
        dialog.style.display = 'none';
    }

    function connectToWifi(ssid) {
        const password = document.getElementById('wifi-password').value;
        fetch('/connect_wifi', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `ssid=${encodeURIComponent(ssid)}&password=${encodeURIComponent(password)}`,
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                toastr.success(data.message);
                closeDialog();
                fetchWifiList(); // 刷新WiFi列表
            } else {
                toastr.error(data.message);
            }
        })
        .catch(error => {
            console.error('连接 WiFi 时出错:', error);
            toastr.error('连接 WiFi 时出错');
        });
    }

    function confirmDisconnect(ssid) {
        if (confirm(`请确认是否断开 ${ssid}。如果你当前除了WiFi没有连接有线网络，断开后可能会导致你的设备无法被访问，你将不得不插入网线来再次操作。`)) {
            disconnectWifi(ssid);
        }
    }

    function disconnectWifi(ssid) {
        fetch('/disconnect_wifi', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `ssid=${encodeURIComponent(ssid)}`,
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                toastr.success(data.message);
                fetchWifiList(); // 刷新WiFi列表
            } else {
                toastr.error(data.message);
            }
        })
        .catch(error => {
            console.error('断开 WiFi 时出错:', error);
            toastr.error('断开 WiFi 时出错');
        });
    }

    // 绑定关闭按钮事件
    document.querySelector('.close-btn').addEventListener('click', closeDialog);
});
