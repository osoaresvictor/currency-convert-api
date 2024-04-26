# Currency Converter API

Este projeto consiste em uma API REST construída em Python utilizando o framework FastAPI. A API oferece dois endpoints principais: um para realizar a conversão entre duas moedas e outro para listar todas as operações de conversão realizadas, associadas a um `user_id` especificado no primeiro endpoint.

## Tecnologias Utilizadas

Foi optado pelo framework **[FastAPI](https://fastapi.tiangolo.com/)** devido à sua otimização para construção de APIs REST em Python, incluindo recursos de documentação automáticos como **[Swagger](https://swagger.io/)** e **[Redoc](https://redocly.github.io/redoc/)**. Para aumentar a velocidade e resiliência, foi feito o uso do serviço de cache **[Redis](https://redis.io/)**, a fim de minimizar a necessidade de repetidos requests HTTP a serviços externos.

A qualidade do código é garantida por ferramentas como **[.editorconfig](https://editorconfig.org/)** e o linter **[Flake8](https://flake8.pycqa.org/en/latest/)**. Adotou-se também as práticas de **[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/#summary)**, que auxiliam a manter a organização, legibilidade e manutenibilidade do repositório.

## Sugestões Futuras
### Arquitetura de Software

Para a execução dos containers, seria um boa approach o uso de [Amazon ECS](https://aws.amazon.com/pt/ecs/) ou, para mais controle, [Amazon EKS](https://aws.amazon.com/pt/eks/). Em termos de observabilidade, por se tratar de uma aplicação relativamente pequena/simples, [Grafana](https://grafana.com/) com [Loki](https://grafana.com/oss/loki/) para logs e [Prometheus](https://prometheus.io/) para métricas seriam boas opções. Acerca de autenticação/autorização, empregar o uso do [Amazon Cognito](https://aws.amazon.com/pt/cognito/) que pode exercer essa função juntamente com o uso do [Amazon API Gateway](https://aws.amazon.com/pt/api-gateway/) seria uma decisão consideravel. Embora um banco de dados SQLite seja suficiente para este projeto de demonstração, alternativas como [DynamoDB](https://aws.amazon.com/pt/dynamodb/) ou [MongoDB](https://www.mongodb.com/) garantem segurança e podem oferecer outras vantagens como desempenho superior e organização, por exemplo.
A imagem a seguir oferece uma representação das sugestões colocadas no parágrafo anterior.

![System Architecture Diagram](SystemDesign.png)

### Codificação e Fluxo de Entrega
Primeiramente, é essencial para qualidade de qualquer software, uma ótima cobertura do código por testes de unidade, testes de integração e a titulo de aperfeiçoamento, testes de contrato também seriam bem vindos. Já sobre CI/CD, um bom pipeline de build e deploy que integre processos de verificação de lint, execução de testes, verificação de cobertura de código com ferramentas como [CodeCov](https://about.codecov.io/) e se possível o uso do [SonarQUBE](https://www.sonarsource.com/products/sonarqube/) que atua auxiliando na detecção de problemas de desenvolvimento como code smells, segurança e/ou bugs, seria excelente.

## Instruções para Execução

1. Clone o projeto para sua máquina.
2. Abra o arquivo `docker-compose.yaml` e substitua `API_URL` por `http://api.exchangeratesapi.io/v1/latest` e `API_ACCESS_KEY` por `sua_chave_de_acesso`.
3. Execute o comando `docker-compose up` na pasta raiz do projeto e aguarde a finalização do processo.
4. Acesse `http://localhost:8000/docs` para visualizar a interface Swagger com um cliente HTTP de teste e a documentação completa, ou `http://localhost:8000/redoc` para uma visualização alternativa com Redoc.
