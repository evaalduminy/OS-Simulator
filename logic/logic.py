# logic.py (FIXED to accept preemptive flag)
import collections

# --- 1. FCFS (First-Come, First-Served) ---
def run_fcfs_logic(processes_data):
    sorted_processes = sorted(processes_data, key=lambda x: x['arrival'])
    current_time = 0
    results = []
    gantt_data = []
    for p in sorted_processes:
        if current_time < p['arrival']:
            gantt_data.append({'pid': 'خمول', 'start': current_time, 'finish': p['arrival']})
            current_time = p['arrival']
        
        result_p = p.copy()
        result_p['start_time'] = current_time
        result_p['completion_time'] = current_time + p['burst']
        result_p['turnaround_time'] = result_p['completion_time'] - p['arrival']
        result_p['waiting_time'] = result_p['start_time'] - p['arrival']
        results.append(result_p)
        gantt_data.append({'pid': p['pid'], 'start': result_p['start_time'], 'finish': result_p['completion_time']})
        current_time = result_p['completion_time']
    
    total_tat = sum(p['turnaround_time'] for p in results)
    total_wt = sum(p['waiting_time'] for p in results)
    avg_tat = total_tat / len(results) if results else 0
    avg_wt = total_wt / len(results) if results else 0
    return results, gantt_data, avg_tat, avg_wt

# --- 2. SJF / SRTF (Shortest Job First / Shortest Remaining Time First) ---
def run_sjf_logic(processes_data, is_preemptive):
    if not is_preemptive:
        return _run_sjf_non_preemptive(processes_data)
    else:
        return _run_srtf_preemptive(processes_data)

def _run_sjf_non_preemptive(processes_data):
    remaining_processes = sorted(processes_data, key=lambda x: x['arrival'])
    current_time = 0
    results = []
    gantt_data = []
    while remaining_processes:
        available_processes = [p for p in remaining_processes if p['arrival'] <= current_time]
        if not available_processes:
            next_arrival_time = remaining_processes[0]['arrival']
            gantt_data.append({'pid': 'خمول', 'start': current_time, 'finish': next_arrival_time})
            current_time = next_arrival_time
            continue
        
        shortest_job = min(available_processes, key=lambda x: x['burst'])
        result_p = shortest_job.copy()
        result_p['start_time'] = current_time
        result_p['completion_time'] = current_time + shortest_job['burst']
        result_p['turnaround_time'] = result_p['completion_time'] - shortest_job['arrival']
        result_p['waiting_time'] = result_p['start_time'] - shortest_job['arrival']
        results.append(result_p)
        gantt_data.append({'pid': shortest_job['pid'], 'start': result_p['start_time'], 'finish': result_p['completion_time']})
        current_time = result_p['completion_time']
        remaining_processes.remove(shortest_job)
    
    total_tat = sum(p['turnaround_time'] for p in results)
    total_wt = sum(p['waiting_time'] for p in results)
    avg_tat = total_tat / len(results) if results else 0
    avg_wt = total_wt / len(results) if results else 0
    return results, gantt_data, avg_tat, avg_wt

def _run_srtf_preemptive(processes_data):
    processes = sorted(processes_data, key=lambda p: p['arrival'])
    gantt_data, results_map = [], {}
    current_time, completed = 0, 0
    remaining_burst = {p['pid']: p['burst'] for p in processes}
    
    while completed < len(processes):
        available = [p for p in processes if p['arrival'] <= current_time and remaining_burst[p['pid']] > 0]
        if not available:
            next_arrival = min([p['arrival'] for p in processes if remaining_burst[p['pid']] > 0])
            if next_arrival > current_time:
                gantt_data.append({'pid': 'خمول', 'start': current_time, 'finish': next_arrival})
            current_time = next_arrival
            continue

        shortest = min(available, key=lambda p: remaining_burst[p['pid']])
        pid = shortest['pid']

        if not gantt_data or gantt_data[-1]['pid'] != pid:
            gantt_data.append({'pid': pid, 'start': current_time, 'finish': current_time + 1})
        else:
            gantt_data[-1]['finish'] += 1

        remaining_burst[pid] -= 1
        current_time += 1

        if remaining_burst[pid] == 0:
            completed += 1
            p_copy = shortest.copy()
            p_copy['completion_time'] = current_time
            p_copy['turnaround_time'] = p_copy['completion_time'] - p_copy['arrival']
            p_copy['waiting_time'] = p_copy['turnaround_time'] - p_copy['burst']
            results_map[pid] = p_copy

    final_results = [results_map[p['pid']] for p in processes]
    total_tat = sum(p['turnaround_time'] for p in final_results)
    total_wt = sum(p['waiting_time'] for p in final_results)
    avg_tat = total_tat / len(final_results) if final_results else 0
    avg_wt = total_wt / len(final_results) if final_results else 0
    return final_results, gantt_data, avg_tat, avg_wt

# --- 3. Priority ---
def run_priority_logic(processes_data, is_preemptive):
    if not is_preemptive:
        return _run_priority_non_preemptive(processes_data)
    else:
        return _run_priority_preemptive(processes_data)

def _run_priority_non_preemptive(processes_data):
    remaining_processes = sorted(processes_data, key=lambda x: x['arrival'])
    current_time = 0
    results = []
    gantt_data = []
    while remaining_processes:
        available_processes = [p for p in remaining_processes if p['arrival'] <= current_time]
        if not available_processes:
            next_arrival_time = remaining_processes[0]['arrival']
            gantt_data.append({'pid': 'خمول', 'start': current_time, 'finish': next_arrival_time})
            current_time = next_arrival_time
            continue
        
        highest_priority_process = min(available_processes, key=lambda x: x['priority'])
        result_p = highest_priority_process.copy()
        result_p['start_time'] = current_time
        result_p['completion_time'] = current_time + highest_priority_process['burst']
        result_p['turnaround_time'] = result_p['completion_time'] - highest_priority_process['arrival']
        result_p['waiting_time'] = result_p['start_time'] - highest_priority_process['arrival']
        results.append(result_p)
        gantt_data.append({'pid': highest_priority_process['pid'], 'start': result_p['start_time'], 'finish': result_p['completion_time']})
        current_time = result_p['completion_time']
        remaining_processes.remove(highest_priority_process)
    
    total_tat = sum(p['turnaround_time'] for p in results)
    total_wt = sum(p['waiting_time'] for p in results)
    avg_tat = total_tat / len(results) if results else 0
    avg_wt = total_wt / len(results) if results else 0
    return results, gantt_data, avg_tat, avg_wt

def _run_priority_preemptive(processes_data):
    processes = sorted(processes_data, key=lambda p: p['arrival'])
    gantt_data, results_map = [], {}
    current_time, completed = 0, 0
    remaining_burst = {p['pid']: p['burst'] for p in processes}
    
    while completed < len(processes):
        available = [p for p in processes if p['arrival'] <= current_time and remaining_burst[p['pid']] > 0]
        if not available:
            next_arrival = min([p['arrival'] for p in processes if remaining_burst[p['pid']] > 0])
            if next_arrival > current_time:
                gantt_data.append({'pid': 'خمول', 'start': current_time, 'finish': next_arrival})
            current_time = next_arrival
            continue

        highest_priority = min(available, key=lambda p: p['priority'])
        pid = highest_priority['pid']

        if not gantt_data or gantt_data[-1]['pid'] != pid:
            gantt_data.append({'pid': pid, 'start': current_time, 'finish': current_time + 1})
        else:
            gantt_data[-1]['finish'] += 1

        remaining_burst[pid] -= 1
        current_time += 1

        if remaining_burst[pid] == 0:
            completed += 1
            p_copy = highest_priority.copy()
            p_copy['completion_time'] = current_time
            p_copy['turnaround_time'] = p_copy['completion_time'] - p_copy['arrival']
            p_copy['waiting_time'] = p_copy['turnaround_time'] - p_copy['burst']
            results_map[pid] = p_copy

    final_results = [results_map[p['pid']] for p in processes]
    total_tat = sum(p['turnaround_time'] for p in final_results)
    total_wt = sum(p['waiting_time'] for p in final_results)
    avg_tat = total_tat / len(final_results) if final_results else 0
    avg_wt = total_wt / len(final_results) if final_results else 0
    return final_results, gantt_data, avg_tat, avg_wt

# --- 4. Round Robin ---
def run_rr_logic(processes_data, quantum):
    ready_queue = collections.deque()
    remaining_burst = {p['pid']: p['burst'] for p in processes_data}
    processes = sorted(processes_data, key=lambda x: x['arrival'])
    current_time = 0
    results = {p['pid']: p.copy() for p in processes_data}
    gantt_data = []
    
    processes_idx = 0
    while processes_idx < len(processes) or ready_queue:
        while processes_idx < len(processes) and processes[processes_idx]['arrival'] <= current_time:
            ready_queue.append(processes[processes_idx])
            processes_idx += 1
        
        if not ready_queue:
            if processes_idx < len(processes):
                next_arrival_time = processes[processes_idx]['arrival']
                gantt_data.append({'pid': 'خمول', 'start': current_time, 'finish': next_arrival_time})
                current_time = next_arrival_time
            continue

        current_process = ready_queue.popleft()
        pid = current_process['pid']
        
        time_slice = min(quantum, remaining_burst[pid])
        gantt_data.append({'pid': pid, 'start': current_time, 'finish': current_time + time_slice})
        current_time += time_slice
        remaining_burst[pid] -= time_slice

        while processes_idx < len(processes) and processes[processes_idx]['arrival'] <= current_time:
            ready_queue.append(processes[processes_idx])
            processes_idx += 1

        if remaining_burst[pid] > 0:
            ready_queue.append(current_process)
        else:
            results[pid]['completion_time'] = current_time
            results[pid]['turnaround_time'] = results[pid]['completion_time'] - results[pid]['arrival']
            results[pid]['waiting_time'] = results[pid]['turnaround_time'] - results[pid]['burst']
    
    final_results = list(results.values())
    total_tat = sum(p['turnaround_time'] for p in final_results)
    total_wt = sum(p['waiting_time'] for p in final_results)
    avg_tat = total_tat / len(final_results) if final_results else 0
    avg_wt = total_wt / len(final_results) if final_results else 0
    return final_results, gantt_data, avg_tat, avg_wt
