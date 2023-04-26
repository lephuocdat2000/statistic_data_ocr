import argparse
import json
import os
import numpy as np
import plotly.express as px
import pandas as pd
from pathlib import Path
from utils import convertpoly2rect, load_yaml
from collections import defaultdict


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("data_path")
    parser.add_argument("--pattern")
    parser.add_argument("--config-path", default="config.yaml")
    parser.add_argument("--output-path", default="outputs")
    parser.add_argument("--export-visualize", action='store_true')
    parser.add_argument("--visualize-on-local-server", action='store_true')
    args = parser.parse_args()

    data_path = args.data_path
    json_glob_paths = list(Path(data_path).glob(args.pattern))
    assert len(json_glob_paths), "Have no data to analyze"

    config = load_yaml(args.config_path)
    get_fields = config.get("get_fields", None)
    if get_fields is None:
        get_all_fields = True
    else:
        get_all_fields = False
    # get statistic
    field_statistic = {}

    for json_glob_path in json_glob_paths:
        with open(str(json_glob_path), "r") as f:
            data = json.load(f)
        f.close()

        num_parent = len(args.pattern.split("/")) - 1
        json_path = json_glob_path
        json_name = json_path.name
        while num_parent > 0:
            json_path = json_path.parent
            json_name = os.path.join(json_path.name, json_name)
            num_parent -= 1
        imageHeight = data["imageHeight"]
        imageWidth = data["imageWidth"]
        for field_info in data["shapes"]:
            if not get_all_fields and (
                "label" not in field_info or field_info["label"] not in get_fields
            ):
                continue
            field_name = field_info["label"]
            if field_name not in field_statistic:
                field_statistic[field_name] = defaultdict(list)
            field_coordinate_rect = convertpoly2rect(np.array(field_info["points"]))
            x_middle = field_coordinate_rect[0] + field_coordinate_rect[2] / 2
            y_middle = field_coordinate_rect[1] + field_coordinate_rect[3] / 2
            x_middle_ratio = x_middle / imageWidth
            y_middle_ratio = y_middle / imageHeight
            field_statistic[field_name]["x"].append(x_middle_ratio)
            field_statistic[field_name]["y"].append(y_middle_ratio)
            field_statistic[field_name]["filename"].append(json_name)

    # visualize
    for field_name, field_info in field_statistic.items():
        x_coordinates = field_info["x"]
        y_coordinates = field_info["y"]
        file_names = field_info["filename"]
        df = pd.DataFrame(
            dict(
                x_coordinates=x_coordinates,
                y_coordinates=y_coordinates,
                file_names=file_names,
                # field_names=field_name*len(x_coordinates)
            )
        )
        fig = px.scatter(
            df,
            x="x_coordinates",
            y="y_coordinates",
            title=field_name,
            hover_data="file_names",
        )
        out_fig_dir = Path(args.output_path)
        if not out_fig_dir.is_dir():
            out_fig_dir.mkdir()
        if args.visualize_on_local_server:
            fig.show()
        if args.export_visualize:
            fig.write_image(Path(out_fig_dir).joinpath(field_name + ".png"))
