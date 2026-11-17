from PIL import Image
import os

def eh_escuro(pixel, limiar=160):
    r, g, b = pixel[:3]
    return r < limiar and g < limiar and b < limiar

def encontrar_cabecalhos_enem(imagem):
    largura, altura = imagem.size
    pixels = imagem.load()
    
    # Região horizontal onde fica o pente (de 40% até 95% da largura da imagem)
    x_inicio = int(largura * 0.40)
    x_fim = int(largura * 0.95)
    largura_regiao = x_fim - x_inicio
    
    posicoes_corte = []
    y = 0
    
    while y < altura - 25:
        # CAMADA 1: Verifica se a linha Y é a barra sólida do topo do pente (>75% escura)
        escuros_topo = sum(1 for x in range(x_inicio, x_fim) if eh_escuro(pixels[x, y]))
        
        if escuros_topo > largura_regiao * 0.75:
            # CAMADA 2: Verifica 4 pixels abaixo se existem os dentinhos (muitas alternâncias)
            transicoes_dentes = 0
            anterior = eh_escuro(pixels[x_inicio, y + 4])
            for x in range(x_inicio + 1, x_fim):
                atual = eh_escuro(pixels[x, y + 4])
                if atual != anterior:
                    transicoes_dentes += 1
                    anterior = atual
            
            # CAMADA 3: Verifica 16 pixels abaixo se a direita está vazia/branca (<5% escura)
            escuros_baixo = sum(1 for x in range(x_inicio, x_fim) if eh_escuro(pixels[x, y + 16]))
            
            if transicoes_dentes >= 35 and escuros_baixo < largura_regiao * 0.05:
                posicao_corte = max(0, y - 10)  # Corta 10 pixels acima do topo do pente
                posicoes_corte.append(posicao_corte)
                print(f"Questão encontrada! Topo em y={y} (dentes={transicoes_dentes}) -> Cortando em y={posicao_corte}")
                
                # Pula 250 pixels para baixo para não cortar a mesma questão de novo
                y += 250
                continue
        y += 1
        
    return posicoes_corte

def dividir_imagem_enem(caminho_imagem, pasta_saida):
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    posicoes_corte = encontrar_cabecalhos_enem(imagem)
    
    if not posicoes_corte:
        print("Nenhuma questão encontrada! Verifique o contraste ou a largura da região.")
        return
    
    print(f"\nTotal de cortes encontrados: {len(posicoes_corte)}")
    os.makedirs(pasta_saida, exist_ok=True)
    
    pontos = [0] + posicoes_corte + [altura]
    contador = 1
    
    for i in range(len(pontos) - 1):
        y_inicio = pontos[i]
        y_fim = pontos[i + 1]
        
        # Ignora sobras pequenas antes da primeira questão
        if y_fim - y_inicio < 100:
            continue
            
        secao = imagem.crop((0, y_inicio, largura, y_fim))
        nome_arquivo = f"questao_{contador:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        contador += 1

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"
    pasta_saida = "questoes"
    
    dividir_imagem_enem(caminho_imagem, pasta_saida)
    print("\nDivisão concluída!")
