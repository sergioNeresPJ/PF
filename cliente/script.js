document.addEventListener('DOMContentLoaded', function() {
    const formSubmit = document.getElementById('formSubmit');
    const recordsBody = document.getElementById('recordsBody');

    formSubmit.addEventListener('submit', function(event) {
        event.preventDefault(); // Evita o comportamento padrão de envio do formulário

        const formData = new FormData(formSubmit);
        const x = formData.get('x');
        const y = formData.get('y');

        // Enviar os valores de x e y para o balanceador de carga
        fetch('http://localhost:5000/calculate_power', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 'x': x, 'y': y })
        })
        .then(response => response.json())
        .then(data => console.log(data)) // Lidar com a resposta do servidor
        .catch(error => console.error('Erro:', error));
    });

    // Carregar registros armazenados do balanceador de carga
    fetch('http://localhost:5000/records', {
        headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
    })
    .then(response => {
        console.log('Resposta recebida do servidor:', response);
        return response.json();
    })
    .then(records => {
        console.log('Registros recebidos:', records);
        recordsBody.innerHTML = '';
        records.forEach(record => {
            const row = document.createElement('tr');
            console.log('Criando nova linha da tabela:', row);
            row.innerHTML = `
                    <td>${record.projetoSD.timestamp}</td>
                    <td>${record.projetoSD.a}</td>
                    <td>${record.projetoSD.b}</td>
                    <td>${record.projetoSD.resultado}</td>
                    <td>${record.projetoSD.microservice}</td>
                `;
            recordsBody.appendChild(row);
            console.log('Linha da tabela adicionada com sucesso:', row);
        });
    })
    .catch(error => console.error('Erro ao carregar registros:', error));

});
