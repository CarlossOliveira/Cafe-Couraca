# ================================================================================================
# FRONTEND DOCKERFILE - React + Vite
# ================================================================================================

# Use uma imagem oficial do Node.js
FROM node:22-alpine

# Define variáveis de ambiente
ENV NODE_ENV=development

# Define o diretório de trabalho no container
WORKDIR /app

# Copia os arquivos de dependências primeiro (melhor cache do Docker)
COPY package*.json ./

# Instala as dependências
RUN npm install

# Copia todo o código do frontend
COPY . .

# Expõe a porta 5173 (porta padrão do Vite)
EXPOSE 5173

# Comando para iniciar o servidor de desenvolvimento
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
