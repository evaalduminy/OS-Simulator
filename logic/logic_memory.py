# logic_memory.py

class MemoryManager:
    def __init__(self, total_size):
        self.total_size = total_size
        # Memory is a list of blocks. Each block is a dict.
        # A block can be {'id': 1, 'start': 0, 'size': 100, 'status': 'free', 'process_id': None, 'internal_frag': 0}
        self.memory = [{'id': 0, 'start': 0, 'size': total_size, 'status': 'free', 'process_id': None, 'internal_frag': 0}]
        self.next_block_id = 1
        self.next_process_id_num = 1

    def add_process(self, size):
        process = {'id': f"P{self.next_process_id_num}", 'size': size, 'status': 'waiting'}
        self.next_process_id_num += 1
        return process

    def _find_first_fit(self, process_size):
        for block in self.memory:
            if block['status'] == 'free' and block['size'] >= process_size:
                return block
        return None

    def _find_best_fit(self, process_size):
        best_block = None
        min_diff = float('inf')
        for block in self.memory:
            if block['status'] == 'free' and block['size'] >= process_size:
                diff = block['size'] - process_size
                if diff < min_diff:
                    min_diff = diff
                    best_block = block
        return best_block

    def _find_worst_fit(self, process_size):
        worst_block = None
        max_diff = -1
        for block in self.memory:
            if block['status'] == 'free' and block['size'] >= process_size:
                diff = block['size'] - process_size
                if diff > max_diff:
                    max_diff = diff
                    worst_block = block
        return worst_block

    def allocate(self, process, algorithm):
        process_size = process['size']
        
        if algorithm == 'First-Fit':
            target_block = self._find_first_fit(process_size)
        elif algorithm == 'Best-Fit':
            target_block = self._find_best_fit(process_size)
        elif algorithm == 'Worst-Fit':
            target_block = self._find_worst_fit(process_size)
        else:
            return None, "الخوارزمية غير معروفة"

        if target_block is None:
            return None, f"لا توجد كتلة ذاكرة كافية للعملية {process['id']} بحجم {process_size}KB"

        # Logic to split the block if there is remaining space
        remaining_size = target_block['size'] - process_size
        
        target_block['status'] = 'allocated'
        target_block['process_id'] = process['id']
        
        if remaining_size > 0:
            target_block['size'] = process_size
            target_block['internal_frag'] = 0 # No internal fragmentation if we split
            
            new_block = {
                'id': self.next_block_id,
                'start': target_block['start'] + process_size,
                'size': remaining_size,
                'status': 'free',
                'process_id': None,
                'internal_frag': 0
            }
            self.next_block_id += 1
            
            # Find index of target_block and insert the new_block after it
            idx = self.memory.index(target_block)
            self.memory.insert(idx + 1, new_block)
        else:
            # If the block fits perfectly, there is no internal fragmentation
            target_block['internal_frag'] = 0

        process['status'] = 'running'
        return target_block, f"تم تخصيص العملية {process['id']} في الكتلة {target_block['id']}"

    def free(self, block_id):
        target_block = next((b for b in self.memory if b['id'] == block_id), None)
        if not target_block or target_block['status'] == 'free':
            return "خطأ: الكتلة غير مخصصة أو غير موجودة"

        freed_process_id = target_block['process_id']
        target_block['status'] = 'free'
        target_block['process_id'] = None
        target_block['internal_frag'] = 0
        
        # Coalesce (merge) with adjacent free blocks
        self._coalesce_memory()
        
        return f"تم تحرير الذاكرة من العملية {freed_process_id}"

    def _coalesce_memory(self):
        # Sort by start address to ensure we check adjacent blocks correctly
        self.memory.sort(key=lambda b: b['start'])
        i = 0
        while i < len(self.memory) - 1:
            current_block = self.memory[i]
            next_block = self.memory[i+1]
            if current_block['status'] == 'free' and next_block['status'] == 'free':
                current_block['size'] += next_block['size']
                self.memory.pop(i+1)
                # Do not increment i, check again in case the new merged block can merge with the next one
            else:
                i += 1

    def get_fragmentation(self):
        total_free_memory = sum(b['size'] for b in self.memory if b['status'] == 'free')
        largest_free_block = max([b['size'] for b in self.memory if b['status'] == 'free'] or [0])
        
        # External fragmentation exists if there's enough total free memory for a process,
        # but it's not contiguous. We define it as the difference.
        external_frag = total_free_memory - largest_free_block
        
        return external_frag
