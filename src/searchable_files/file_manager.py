import subprocess


def copy_files(source_dir, target_dir):
    # Create the target directory
    subprocess.run(['mkdir', '-p', target_dir], check=True)

    # Copy all files from source to target directory
    try:
        subprocess.run(['cp', '-r', f"{source_dir}/.", target_dir], check=True)
        print(f"Successfully copied all files from {source_dir} to {target_dir}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to copy files: {e}")
        return False
