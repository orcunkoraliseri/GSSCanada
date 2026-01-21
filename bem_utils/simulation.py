import os
import subprocess
import platform
import shutil
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

def run_simulation(idf_path, epw_path, output_dir, ep_path, n_jobs=1, quiet=False):
    """
    Runs a single EnergyPlus simulation.
    
    Args:
        idf_path: Path to the IDF file
        epw_path: Path to the EPW weather file
        output_dir: Directory to store simulation outputs
        ep_path: Path to EnergyPlus executable or directory
        n_jobs: Number of threads for this simulation (internal E+ parallelism)
        quiet: If True, suppress verbose output (useful for parallel runs)
    
    Returns:
        dict: {'success': bool, 'name': str, 'message': str}
    """
    name = os.path.basename(idf_path)
    
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Determine executable extension based on platform
        exe_ext = '.exe' if platform.system() == 'Windows' else ''
            
        # If ep_path is a directory, look for energyplus executable
        if os.path.isdir(ep_path):
            ep_dir = ep_path
            ep_exe = os.path.join(ep_path, f'energyplus{exe_ext}')
        else:
            ep_dir = os.path.dirname(ep_path)
            ep_exe = ep_path
            
        if not os.path.exists(ep_exe):
            msg = f"Error: EnergyPlus executable not found at {ep_exe}"
            if not quiet:
                print(msg)
            return {'success': False, 'name': name, 'message': msg}

        # Prepare for ExpandObjects
        in_idf_path = os.path.join(output_dir, 'in.idf')
        shutil.copy2(idf_path, in_idf_path)

        # Copy Energy+.idd to output directory for ExpandObjects
        idd_path = os.path.join(ep_dir, 'Energy+.idd')
        if os.path.exists(idd_path):
            shutil.copy2(idd_path, os.path.join(output_dir, 'Energy+.idd'))
        elif not quiet:
            print(f"Warning: Energy+.idd not found at {idd_path}. ExpandObjects might fail.")
        
        expand_objects_exe = os.path.join(ep_dir, f'ExpandObjects{exe_ext}')
        if os.path.exists(expand_objects_exe):
            # if not quiet:
            #     print(f"Running ExpandObjects in {output_dir}")
            subprocess.run([expand_objects_exe], cwd=output_dir, check=True,
                          capture_output=quiet)
        
        # Check if expanded.idf was created
        expanded_idf_path = os.path.join(output_dir, 'expanded.idf')
        if os.path.exists(expanded_idf_path):
            simulation_idf_path = expanded_idf_path
        else:
            simulation_idf_path = in_idf_path

        # Build EnergyPlus command
        cmd = [
            ep_exe,
            '-w', epw_path,
            '-d', output_dir,
        ]
        
        if n_jobs > 1:
            cmd.extend(['-j', str(n_jobs)])
            
        cmd.append(simulation_idf_path)
        
        if not quiet:
            print(f"Running simulation for {name}...")
        
        subprocess.run(cmd, check=True, capture_output=quiet)
        
        msg = f"Simulation completed successfully: {name}"
        if not quiet:
            print(msg)
        return {'success': True, 'name': name, 'message': msg, 'output_dir': output_dir}
        
    except subprocess.CalledProcessError as e:
        msg = f"Simulation failed: {name} - {e}"
        if not quiet:
            print(msg)
        return {'success': False, 'name': name, 'message': msg, 'output_dir': output_dir}
    except Exception as e:
        msg = f"Unexpected error for {name}: {e}"
        if not quiet:
            print(msg)
        return {'success': False, 'name': name, 'message': msg, 'output_dir': output_dir}


def _run_simulation_wrapper(args):
    """Wrapper function for parallel execution (required for ProcessPoolExecutor)."""
    # Use verbose mode for single simulations
    quiet = args.get('quiet', True)
    return run_simulation(
        idf_path=args['idf'],
        epw_path=args['epw'],
        output_dir=args['output_dir'],
        ep_path=args['ep_path'],
        n_jobs=args.get('n_jobs', 1),
        quiet=quiet
    )


def run_simulations_parallel(simulation_jobs, ep_path, max_workers=None):
    """
    Run multiple EnergyPlus simulations in parallel.
    
    Args:
        simulation_jobs: List of dicts, each containing:
            - 'idf': Path to IDF file
            - 'epw': Path to EPW weather file
            - 'output_dir': Output directory for this simulation
            - 'name': Display name (optional)
        ep_path: Path to EnergyPlus executable or directory
        max_workers: Maximum number of concurrent simulations (default: CPU count)
    
    Returns:
        dict: {'successful': List[str], 'failed': List[str], 'total_time': float}
    """
    
    if max_workers is None:
        max_workers = os.cpu_count() or 4
    
    # Limit workers to number of jobs
    max_workers = min(max_workers, len(simulation_jobs))
    
    # Add ep_path to each job
    jobs = []
    # Use verbose mode for single simulations
    use_quiet = len(simulation_jobs) > 1
    for job in simulation_jobs:
        job_copy = job.copy()
        job_copy['ep_path'] = ep_path
        job_copy['n_jobs'] = 1  # Use 1 thread per simulation when running in parallel
        job_copy['quiet'] = use_quiet
        jobs.append(job_copy)
    
    print(f"\n{'='*60}")
    print(f"Starting {len(jobs)} simulations with {max_workers} parallel workers")
    print(f"{'='*60}\n")
    
    successful = []
    failed = []
    start_time = time.time()
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all jobs
        future_to_job = {executor.submit(_run_simulation_wrapper, job): job for job in jobs}
        
        # Process completed jobs
        completed = 0
        for future in as_completed(future_to_job):
            completed += 1
            job = future_to_job[future]
            job_name = job.get('name', os.path.basename(job['idf']))
            
            try:
                result = future.result()
                if result['success']:
                    successful.append(result)
                    status = "✓"
                else:
                    failed.append(result)
                    status = "✗"
                print(f"[{completed}/{len(jobs)}] {status} {job_name}")
            except Exception as e:
                failed.append({'name': job_name, 'message': str(e), 'success': False})
                print(f"[{completed}/{len(jobs)}] ✗ {job_name} - Exception: {e}")
    
    elapsed = time.time() - start_time
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"SIMULATION SUMMARY")
    print(f"{'='*60}")
    print(f"Total time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
    print(f"Successful: {len(successful)}/{len(jobs)}")
    print(f"Failed: {len(failed)}/{len(jobs)}")
    
    return {
        'successful': successful,
        'failed': failed,
        'total_time': elapsed
    }
