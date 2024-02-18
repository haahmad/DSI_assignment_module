Tests to run manually
=====================

1. Initialize Analysis with an empty string -> confirm exception
2. Initiailize Analysis with a path to a file that does not exist -> confirm exception
3. Remove a key config value for load_date (api_base_path in configs/job_config.yml), call load_data
4. Attempt to compute_analysis before calling load_data -> confirm exception
5. Remove ntfy_topic value from configs/system_config.yml, call ntfy_topic -> confirm exception
6. Disconnect internet connection -> call load_data -> confirm fetch fails, exception raised
7. Subsribe to ntfy.sh topic configured in configs/system_config.yml, call notify_done -> confirm message published on ntfy.sh