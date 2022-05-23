# Atividade banco distribuído

Documentação do projeto no arquivo `doc.pdf`

## Estrutura de arquivos

mock_data.py: é o arquivo que simula um banco de dados na memória da aplicação em execução.
data_server.py: é o servidor que controla as operações no mock_data.py
business_serber: é o sevidor de negócio, que resopnde as chamadas do cliente e faz requisições para o servidor de dados.
log.txt: é um arquivo que registra as ações dos clientes no servidor de dados. Todas as operaçòes são registradas no formato: TIMESTAMP NumOperacao IdServidorNegocio TipoOperacao Conta Valor
client1.py: é uma simulação de um conjunto de operações realizadas pelos __clients__.

