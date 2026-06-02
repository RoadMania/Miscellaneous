import pandas as pd
import sys

df = None

def load_data():
    global df
    try:
        df = pd.read_csv('dataset.csv', encoding='utf-8')
        print(f"Загружено {df.shape[0]} строк, {df.shape[1]} колонок")
    except FileNotFoundError:
        print("Ошибка: файл dataset.csv не найден")
        sys.exit(1)

def analyze_data():
    with open('report.txt', 'w', encoding='utf-8') as f:
        def pr(*args):
            print(*args)
            print(*args, file=f)
        
        pr("ОТЧЕТ")
        
        pr(f"\nРазмер: {df.shape[0]} строк x {df.shape[1]} колонок")
        
        pr("\nКолонки и типы данных:")
        for col in df.columns:
            pr(f"  {col}: {df[col].dtype}")
        
        pr("\nПропуски:")
        for col in df.columns:
            nulls = df[col].isnull().sum()
            if nulls > 0:
                pr(f"  {col}: {nulls}")
            else:
                pr(f"  {col}: нет")
        
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        if 'Year' in num_cols:
            num_cols.remove('Year')
        
        if num_cols:
            pr("\nСтатистика по числам:")
            for col in num_cols:
                pr(f"  {col}: среднее={df[col].mean():.2f}, медиана={df[col].median():.2f}, std={df[col].std():.2f}")
        
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        if 'Year' in df.columns:
            cat_cols.append('Year')
        
        if cat_cols:
            pr("\nКатегории:")
            for col in cat_cols:
                pr(f"  {col}:")
                for val, cnt in df[col].value_counts().items():
                    pr(f"    {val}: {cnt}")
    
    print("\nОтчет сохранен в report.txt")

if __name__ == "__main__":
    load_data()
    if df is not None:
        analyze_data()