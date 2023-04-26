# statistic_data_ocr
This repository is created to visualize the distribution of fields in dataset, which help researcher acquires more intuitive knowledge about dataset

1. Install dependencies
    pip install -r requirements.txt
2. List fields which you want to visualize distribution. If you want to visualize all fields then simply ignore this step
3. Run scripts:
    python main.py <data_path> --pattern <pattern to glob json> --export_visualize (if you want to export visualized image) --visualize-on-local-server (if you want to visualize directly on local server)
 