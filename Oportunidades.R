# define a quantidade de RAM que a JVM poderá usar, abaixo está configurado para 7 GB
options(java.parameters = "-Xmx10G")

# bibliotecas usadas
library(r5r)
library(readxl)
library(tidyr)
library(dplyr)
library(writexl)
library(ggplot2)
library(ggrepel)

# criar uma variavel com o path (caminho) de onde seus arquivos estão salvos
path <- getwd()

# cria a rede de transporte multimodal usada em todas as funções do r5r
r5r_core <- setup_r5(data_path = path, verbose = FALSE)

table_minha = read_excel("Oportunidades_3kms.xlsx")

table_minha = table_minha %>% 
  rename(id = Nome,
         lat = Latitude,
         lon = Longitude) %>% 
  distinct(id,.keep_all = TRUE)

create_accessibility_df <- function(mode, times, table_minha) {
  access_list <- lapply(times, function(time) {
    accessibility(
      r5r_core,
      origins = table_minha[1, ],
      destinations = table_minha,
      opportunities_colnames = colnames(table_minha)[5:22],
      mode = mode,
      decay_function = "step",
      cutoffs = time,
      max_trip_duration = time
    ) %>% mutate(Total = sum(accessibility), Mode = mode, Time = time)
  })
  do.call(rbind, access_list)
}


# Cria dataframes de acessibilidade para cada modal
access_bicicleta <- create_accessibility_df("BICYCLE", seq(3,30,3), table_minha)
access_pedestre <- create_accessibility_df("WALK", seq(3,30,3), table_minha)
access_carro <- create_accessibility_df("CAR", seq(3,30,3), table_minha)

# Consolida todos os dataframes em um único dataframe
access_total <- bind_rows(access_bicicleta, access_pedestre, access_carro)
custom_colors <- c("Bicicleta" = "#3494ba", "Pedestre" = "#7a8c8e", "Carro" = "#75bda7")

access_total <- access_total %>%
  mutate(Mode = recode(Mode, "CAR" = "Carro", "BICYCLE" = "Bicicleta", "WALK" = "Pedestre"))

# Calcular o valor máximo de Total
max_total <- max(access_total$Total)

# Calcular a justificação vertical para evitar que os números sejam cortados
access_total <- access_total %>%
  mutate(label_vjust = ifelse(Total == max_total, -0.7, -0.5),
         label_vjust= ifelse(Total != max_total, -1,-0.5),
         label_vjust = ifelse(Mode == "Carro" & Time == 3, -3, label_vjust),
         label_vjust = ifelse(Mode == "Carro" & Time == 6, -3, label_vjust),
         label_vjust = ifelse(Mode == "Carro" & Time == 15, 2, label_vjust),
         label_vjust = ifelse(Mode == "Pedestre" & Time == 3, -2, label_vjust),
         label_vjust = ifelse(Mode == "Pedestre" & Time == 6, -2, label_vjust),
         label_vjust = ifelse(Mode == "Pedestre" & Time == 9, -2, label_vjust),
         label_vjust = ifelse(Mode == "Bicicleta" & Time == 30, 2, label_vjust)
                              )

# Criar o gráfico
ggplot(access_total, aes(x = Time, y = Total, color = Mode)) +
  geom_line(size = 1.2) +
  geom_point(aes(color = Mode), size = 1, shape = 21, fill = "white", stroke = 1.5) +
  geom_text(aes(label = Total, vjust = label_vjust), size = 2) +
  geom_hline(aes(yintercept = max_total, linetype = "Valor Máximo"), color = "red", size = 1.2) + # Adicionar linha pontilhada no valor máximo
  scale_linetype_manual(name = "", values = c("Valor Máximo" = "dotted")) + # Adicionar a linha pontilhada na legenda
  labs(title = "Acessibilidade por Tempo de Viagem e Modalidade",
       x = "Tempo de Viagem (minutos)",
       y = "Total de Oportunidades",
       color = "Modalidade",
       linetype = "Legenda") +
  scale_color_manual(values = custom_colors) +
  theme_minimal() +
  theme(panel.grid = element_line(color = alpha("black", 0.05)),
        plot.title = element_text(size = 8, face = "bold"),
        axis.title = element_text(size = 6),
        axis.text = element_text(size = 6),
        legend.title = element_text(size = 8),
        legend.text = element_text(size = 6),
        plot.margin = margin(t = 20, r = 20, b = 20, l = 20)) # Ajustar as margens para evitar cortes

ggsave("acessibilidade_por_modal.png",dpi=300)


custom_colors_4 <- c("restaurant" = "#3494ba", "gym" = "#7a8c8e", "café" = "#75bda7", "market" = "#3e3e3e")

access_pedestre_simplificado = access_pedestre %>% filter(opportunity %in% c('restaurant','gym', 'café','market'))

# Função para ajustar a posição vertical dos rótulos


# Aplicar a função de ajuste
access_pedestre_simplificado = access_pedestre_simplificado %>% 
  mutate(label_vjust = -1,
         label_vjust = ifelse(opportunity == "restaurant" & Time == 30, 2, label_vjust),
         label_vjust = ifelse(opportunity == "restaurant" & Time == 3, -3, label_vjust),
         label_vjust = ifelse(opportunity == "gym" & Time == 3, -2, label_vjust),
         label_vjust = ifelse(opportunity == "café" & Time == 3, -1, label_vjust),
         label_vjust = ifelse(opportunity == "market" & Time == 3, 0 , label_vjust),
         label_vjust = ifelse(opportunity == "restaurant" & Time == 6, -3, label_vjust),
         label_vjust = ifelse(opportunity == "gym" & Time == 6, -2.5, label_vjust),
         label_vjust = ifelse(opportunity == "café" & Time == 6, -1.5, label_vjust),
         label_vjust = ifelse(opportunity == "market" & Time == 6, -1 , label_vjust),
         label_vjust = ifelse(opportunity == "restaurant" & Time == 9, -2, label_vjust),
         label_vjust = ifelse(opportunity == "gym" & Time == 9, -3, label_vjust),
         label_vjust = ifelse(opportunity == "café" & Time == 9, -2, label_vjust),
         label_vjust = ifelse(opportunity == "market" & Time == 9, -1 , label_vjust),
         label_vjust = ifelse(opportunity == "restaurant" & Time ==12, -1, label_vjust),
         label_vjust = ifelse(opportunity == "gym" & Time == 12, -3, label_vjust),
         label_vjust = ifelse(opportunity == "café" & Time == 12, -2, label_vjust),
         label_vjust = ifelse(opportunity == "market" & Time == 12, -1 , label_vjust),
         label_vjust = ifelse(opportunity == "restaurant" & Time ==15, -1, label_vjust),
         label_vjust = ifelse(opportunity == "gym" & Time == 15, -3, label_vjust),
         label_vjust = ifelse(opportunity == "café" & Time == 15, -2, label_vjust),
         label_vjust = ifelse(opportunity == "market" & Time == 15, -1 , label_vjust),
         label_vjust = ifelse(opportunity == "restaurant" & Time ==18, -1, label_vjust),
         label_vjust = ifelse(opportunity == "gym" & Time == 18, -3, label_vjust),
         label_vjust = ifelse(opportunity == "café" & Time == 18, -2, label_vjust),
         label_vjust = ifelse(opportunity == "market" & Time == 18, -1 , label_vjust),
         label_vjust = ifelse(opportunity == "restaurant" & Time ==21, -1, label_vjust),
         label_vjust = ifelse(opportunity == "gym" & Time == 21, -3, label_vjust),
         label_vjust = ifelse(opportunity == "café" & Time == 21, -2, label_vjust),
         label_vjust = ifelse(opportunity == "market" & Time == 21, -1 , label_vjust),)


  
# Criar o gráfico
ggplot(access_pedestre_simplificado, aes(x = Time, y = accessibility, color = opportunity)) +
  geom_line(size = 1.2) +
  geom_point(aes(color = opportunity), size = 1, shape = 21, fill = "white", stroke = 1.5) +
  geom_text(aes(label = accessibility, vjust = label_vjust), size = 2.5) +
  labs(title = "Acessibilidade para Pedestres por Tempo de viagem",
       x = "Tempo de Viagem (minutos)",
       y = "Total de Oportunidades",
       color = "Oportunidade") +
  scale_color_manual(values = custom_colors_4) +
  theme_minimal() +
  theme(panel.grid = element_line(color = alpha("black", 0.05)),
        plot.title = element_text(size = 8, face = "bold"),
        axis.title = element_text(size = 6),
        axis.text = element_text(size = 6),
        legend.title = element_text(size = 8),
        legend.text = element_text(size = 6))

ggsave("acessibilidade_por_tipo.png",dpi=300)

