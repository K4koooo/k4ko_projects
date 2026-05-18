import os
from huggingface_hub import hf_hub_download

def main():
    # Definiowanie ścieżki docelowej
    base_dir = os.path.dirname(os.path.abspath(__file__))
    modele_dir = os.path.join(base_dir, 'modele')
    os.makedirs(modele_dir, exist_ok=True)
    
    repo_id = "Qwen/Qwen2.5-3B-Instruct-GGUF"
    filename = "qwen2.5-3b-instruct-q4_k_m.gguf"
    
    print(f"Pobieranie modelu {filename} z repozytorium {repo_id}...")
    print("Może to zająć kilka minut w zależności od Twojego łącza internetowego (rozmiar ok. 2.4 GB).")
    
    try:
        # Pobieranie pliku (huggingface_hub automatycznie użyje cache lub pobierze bezpośrednio)
        downloaded_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=modele_dir,
            local_dir_use_symlinks=False
        )
        print(f"\nSukces! Model został pomyślnie pobrany i zapisany w: {downloaded_path}")
    except Exception as e:
        print(f"\nBłąd podczas pobierania: {str(e)}")
        print("Upewnij się, że masz połączanie z internetem i miejsce na dysku.")

if __name__ == "__main__":
    main()
