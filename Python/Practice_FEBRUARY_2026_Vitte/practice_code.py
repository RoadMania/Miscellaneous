import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("C:\\Users\\***\\Downloads\\dataset.csv", header=None)
print("Первые 5 строк датасета:")
print(df.head())

print(f"Строк: {df.shape[0]}, Столбцов: {df.shape[1]}")

print(df.info())

print("Пропуски:\n", df.isnull().sum())
print("\nДубликаты:", df.duplicated().sum())

df.dropna(subset=[0], inplace=True)

print(f"Итоговое количество строк: {df.shape[0]}")
print(f"Количество столбцов: {df.shape[1]}")

numeric_cols = df.columns[6:15]
print(f"Выбраны колонки: {list(numeric_cols)}")

print("Минимальные значения по числовым колонкам:")
print(df[numeric_cols].min())

print("Максимальные значения по числовым колонкам:")
print(df[numeric_cols].max())

print("Количество уникальных значений в каждой колонке:")
print(df.nunique())

print("Суммы значений по числовым колонкам:")
print(df[numeric_cols].sum())

for col in range(6, 15):
    df[col] = pd.to_numeric(df[col].astype(str).str.replace('.', '', regex=False), errors='coerce')

print("Суммы значений по числовым колонкам:")
print(df[numeric_cols].sum())

plt.figure(figsize=(12, 6))
plt.plot(df.index[:100], df[13][:100], marker='o', linestyle='-', color='b', markersize=3)
plt.title('Динамика показателя (колонка 13) — первые 100 записей')
plt.xlabel('Номер записи')
plt.ylabel('Значение показателя')
plt.grid(True, alpha=0.3)
plt.show()

country_avg = df.groupby(1)[13].mean().sort_values()

plt.figure(figsize=(10, 6))
country_avg.plot(kind='bar', color='skyblue', edgecolor='black')
plt.title('Среднее значение показателя (колонка 13) по странам')
plt.xlabel('Страна')
plt.ylabel('Среднее значение')
plt.xticks(rotation=45)
plt.grid(axis='y', alpha=0.3)
plt.show()

plt.figure(figsize=(8, 6))
plt.scatter(df[10], df[13], alpha=0.5, s=10, c='green')
plt.title('Зависимость между показателями (колонка 10 и колонка 13)')
plt.xlabel('Показатель (колонка 10)')
plt.ylabel('Показатель (колонка 13)')
plt.grid(True, alpha=0.3)
plt.show()

total_sum = df[13].sum()

df[15] = (df[13] / total_sum) * 100

print("Первые 5 строк с новым столбцом:")
print(df[[13, 15]].head())

country_stats = pd.DataFrame({
    'country': df[1].unique(),
    'avg_value': df.groupby(1)[13].mean().values
})

print("Сводный DataFrame по странам:")
print(country_stats)

input("\nНажмите Enter для выхода...")
