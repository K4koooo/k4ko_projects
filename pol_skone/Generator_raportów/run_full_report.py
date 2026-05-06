import os
import subprocess
import sys
import glob

def get_next_report_number(results_dir):
    # Szuka folderów o nazwie Dashboard_N
    existing_folders = glob.glob(os.path.join(results_dir, "Dashboard_*"))
    nums = []
    for folder in existing_folders:
        try:
            name = os.path.basename(folder)
            num = int(name.split('_')[1])
            nums.append(num)
        except (IndexError, ValueError):
            continue
    return max(nums) + 1 if nums else 1

def run_all():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Przygotowanie folderu głównego wyników
    main_output_dir = os.path.join(base_dir, 'Dashboard_Wyniki')
    if not os.path.exists(main_output_dir):
        os.makedirs(main_output_dir)
    
    # Wyznaczenie numeru i ścieżki dla nowego raportu
    report_num = get_next_report_number(main_output_dir)
    report_folder_name = f"Dashboard_{report_num}"
    target_dir = os.path.join(main_output_dir, report_folder_name)
    os.makedirs(target_dir)

    scripts = [
        'standardize_data.py',
        'generate_insights.py',
        'generate_dashboard.py'
    ]

    print(f"--- GENERATOR RAPORTÓW (RAPORT NR {report_num}) ---")
    
    for script in scripts:
        full_path = os.path.join(base_dir, script)
        print(f"\nUruchamiam: {script}...")
        
        # Przekazujemy ścieżkę do folderu docelowego jako argument
        result = subprocess.run([sys.executable, full_path, target_dir], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(result.stdout.strip())
        else:
            print(f"BŁĄD w {script}:")
            print(result.stderr)
            return

    print("\n" + "="*50)
    print(f"PROCES ZAKOŃCZONY SUKCESEM!")
    print(f"WSZYSTKIE PLIKI ZAPISANO W: {target_dir}")
    print("="*50)

if __name__ == "__main__":
    run_all()
