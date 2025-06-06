# 🕵️‍♂️ FakeDetec - Ferramenta de Análise Forense de Imagens

## 📝 Descrição
FakeDetec é uma poderosa ferramenta de linha de comando para detecção de manipulação de imagens e conteúdo gerado por IA. Ela analisa tanto os dados da imagem quanto os metadados para identificar potenciais sinais de adulteração, edição ou geração artificial.

## ✨ Funcionalidades
- 🔍 Análise de metadados (dados EXIF, ferramentas de criação, timestamps)
- 🎨 Detecção de manipulação de imagem
- 🤖 Detecção de conteúdo gerado por IA
- 📊 Análise de Nível de Erro (ELA)
- 🎯 Detecção de cópia e colagem
- 📈 Análise de padrões de ruído
- 🎨 Análise de histograma de cores
- 📝 Geração de relatórios detalhados
- 🎨 Saída colorida no console com arte ASCII
- 🖼️ Extração de frames com marcações de áreas suspeitas

## 🚀 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seuusuario/fakedetec.git
cd fakedetec
```

2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## 💻 Uso

Uso básico:
```bash
python main.py analisar caminho/para/imagem.jpg
```

Analisar múltiplas imagens:
```bash
python main.py analisar caminho/para/diretorio
```

Obter ajuda detalhada:
```bash
python main.py --ajuda
```

## 📊 Saída
Os resultados da análise são salvos no diretório `output`, incluindo:
- Relatórios detalhados de análise
- Marcadores visuais de manipulações detectadas
- Dados estatísticos
- Análise de metadados
- Frames extraídos com marcações de áreas suspeitas

## 🛠️ Detalhes Técnicos
A ferramenta utiliza várias técnicas para detecção:
- Análise de Nível de Erro (ELA)
- Análise de metadados EXIF
- Análise de padrões de ruído
- Análise de histograma de cores
- Detecção de cópia e colagem
- Detecção de artefatos de geração por IA

## 📚 Dependências
- Pillow: Processamento de imagens
- OpenCV: Operações de visão computacional
- scikit-image: Processamento avançado de imagens
- numpy: Operações numéricas
- exif: Extração de metadados
- colorama & rich: Formatação do terminal
- pywavelets: Análise wavelet
- matplotlib: Visualização

## 🤝 Contribuindo
Contribuições são bem-vindas! Por favor, sinta-se à vontade para enviar um Pull Request.

## 📄 Licença
Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.

## ⚠️ Aviso Legal
Esta ferramenta é para fins educacionais e de pesquisa. Os resultados devem ser verificados por especialistas humanos para aplicações críticas. 