import re

"""
PicoComputer Emulator Core
==========================

This module implements the logic for the picoComputer architecture.

Architecture Specs:
- Word Size: 16-bit signed/unsigned integers.
- Memory: 64KB (65536 words).
- Registers:
    * PC: Program Counter
    * SP: Stack Pointer (grows downwards from 65535)
    * General purpose variables stored in Fixed Data Area (Addresses 0-7).
"""


class PicoEmulator:
    """
    The core emulation engine for picoComputer.

    Attributes:
        memory (list): A list of integers representing 64k memory.
        pc (int): Program Counter - points to the next instruction address.
        sp (int): Stack Pointer - points to the top of the stack.
        registers (dict): Map of symbol names to memory addresses (e.g., 'A' -> 1).
        labels (dict): Map of label names to memory addresses for branching.
        instructions (dict): Map of memory addresses to instruction metadata.
        is_running (bool): Flag indicating execution state.
        is_finished (bool): Flag indicating if STOP was reached.
        output_buffer (list): Capture of standard output for the GUI.
        last_error (str): Description of the last runtime error.
    """

    def __init__(self):
        """Initializes the emulator state."""
        self.reset()

    def reset(self):
        """
        Resets the emulator to the initial power-on state.

        Clears memory, resets pointers, and clears internal symbol tables.
        """
        self.memory = [0] * 65536  # 64K memory space
        self.pc = 0  # Program Counter
        self.sp = 65535  # Stack Pointer (starts at end of memory)
        self.registers = {}  # Symbol map (e.g., {"A": 10, "LOOP": 5})
        self.labels = {}  # Jump label map
        self.instructions = {}  # Map: Address -> Instruction Data

        self.is_running = False
        self.is_finished = False

        self.output_buffer = []  # Stores print outputs
        self.last_error = ""

        # Input handling state
        self.input_needed = 0  # Count of inputs required by current instruction
        self.input_dest_addr = 0  # Memory address to store the next input

        # Track modified memory for efficient GUI updates
        self.touched_memory = set()

    def _clamp_16bit(self, value):
        """
        Constrains a value to the 16-bit unsigned integer range (0-65535).

        Args:
            value (int): The arbitrary integer.

        Returns:
            int: The value wrapped modulo 65536.
        """
        return int(value) & 0xFFFF

    def _to_signed(self, value):
        """
        Interprets a 16-bit unsigned value as a signed 16-bit integer (Two's Complement).

        Range: -32768 to 32767.

        Args:
            value (int): The unsigned 16-bit value.

        Returns:
            int: The signed python integer.
        """
        value = value & 0xFFFF
        if value > 32767:
            return value - 65536
        return value

    def parse(self, source_code):
        """
        Parses assembly source code, builds the symbol table, and loads instructions.

        This acts as a simplified assembler. It runs a single pass to collect
        labels, variables, and instructions.

        Args:
            source_code (str): The full assembly string.
        """
        self.reset()
        lines = source_code.split("\n")
        current_address = 0

        # Pass 1: Parsing
        for idx, line in enumerate(lines):
            # Strip comments (after ';') and whitespace
            line = line.split(";")[0].strip()
            if not line:
                continue

            # 1. Variable Definition (e.g., A = 10)
            # This allocates a symbol pointing to a specific value or address.
            if "=" in line:
                parts = line.split("=")
                name = parts[0].strip().upper()
                try:
                    val = int(parts[1].strip())
                    # Store symbol mapping
                    self.registers[name] = val
                    # Initialize memory location if it falls in Fixed Data Area (0-7) or valid memory
                    if 0 <= val < len(self.memory):
                        self.memory[val] = 0
                        self.touched_memory.add(val)
                except ValueError:
                    pass
                continue

            # 2. ORG Directive (e.g., ORG 100)
            # Sets the origin address for the subsequent code.
            if line.upper().startswith("ORG"):
                try:
                    parts = line.split()
                    current_address = int(parts[1])
                    self.pc = current_address  # Set start PC to ORG
                except:
                    pass
                continue

            # 3. Label Definition (e.g., LOOP:)
            # Stores the current address as a jump target.
            if ":" in line:
                label_part, instr_part = line.split(":", 1)
                label_name = label_part.strip().upper()
                self.labels[label_name] = current_address
                line = instr_part.strip()

            # 4. Instruction Store
            # Maps the current address to the raw instruction text for execution.
            if line:
                self.instructions[current_address] = {"text": line, "line_no": idx + 1}
                current_address += 1

    def resolve_symbol(self, token):
        """
        Resolves a string token to a numeric value (Address or Constant).

        Args:
            token (str): The symbol token (e.g., "A", "LOOP", "100").

        Returns:
            int: The resolved numeric value.

        Raises:
            ValueError: If the symbol is not defined.
        """
        token = token.strip().upper()

        # Handle raw numbers (including negative numbers)
        try:
            return int(token)
        except ValueError:
            pass

        # Check symbol tables
        if token in self.registers:
            return self.registers[token]
        if token in self.labels:
            return self.labels[token]

        raise ValueError(f"Unknown symbol: {token}")

    def resolve_value(self, operand):
        """
        Determines the effective value of an operand for calculation (GETTER).

        Handles the three addressing modes of picoComputer:
        1. Indirect: (A) -> Memory[Memory[A]]
        2. Immediate: #A or 100 -> Value of A or 100
        3. Direct: A -> Memory[A]

        Args:
            operand (str): The instruction operand string.

        Returns:
            int: The signed integer value.
        """
        operand = operand.strip().upper()

        # Case 1: Indirect Addressing ((A))
        # Logic: Treat operand as a pointer to a pointer.
        if operand.startswith("(") and operand.endswith(")"):
            inner = operand[1:-1]
            ptr_loc = self.resolve_symbol(inner)
            real_addr = self.memory[ptr_loc]
            if 0 <= real_addr < len(self.memory):
                val = self.memory[real_addr]
                # Return signed value for arithmetic operations logic
                return self._to_signed(val)
            raise ValueError(f"Indirect access out of bounds: {real_addr}")

        # Case 2: Immediate Value (#A or #100)
        # Logic: Use the address/value of the symbol directly, not memory content.
        if operand.startswith("#"):
            return self.resolve_symbol(operand[1:])

        # Case 3: Raw Number
        try:
            return int(operand)
        except ValueError:
            pass

        # Case 4: Direct Addressing (A)
        # Logic: Return the value stored in Memory[A].
        addr = self.resolve_symbol(operand)
        if 0 <= addr < len(self.memory):
            val = self.memory[addr]
            return self._to_signed(val)

        raise ValueError(f"Memory access out of bounds: {addr}")

    def resolve_write_target(self, operand):
        """
        Determines the specific memory INDEX to write result to (SETTER HELPER).

        Args:
            operand (str): The destination operand string.

        Returns:
            int: The memory address index.
        """
        operand = operand.strip().upper()

        # Indirect Write: MOV (A), ... -> Write to address stored in A
        if operand.startswith("(") and operand.endswith(")"):
            inner = operand[1:-1]
            ptr_loc = self.resolve_symbol(inner)  # e.g., 5
            target_addr = self.memory[ptr_loc]  # e.g., 100
            return target_addr

        # Direct Write: MOV A, ... -> Write to address of A
        return self.resolve_symbol(operand)

    def set_value(self, operand, value):
        """
        Writes a value to memory based on the operand type.

        Args:
            operand (str): The destination operand.
            value (int): The value to store.
        """
        dest_addr = self.resolve_write_target(operand)

        if 0 <= dest_addr < len(self.memory):
            # Clamp to 16-bit before storing to simulate register overflow behavior
            clamped_val = self._clamp_16bit(value)
            self.memory[dest_addr] = clamped_val
            self.touched_memory.add(dest_addr)
        else:
            raise ValueError(f"Memory write out of bounds: {dest_addr}")

    def provide_input(self, value):
        """
        Receives input from the GUI for the IN instruction.

        Args:
            value (str): The string value from the UI input field.

        Returns:
            bool: True if input was valid and accepted, False otherwise.
        """
        if self.input_needed > 0:
            try:
                val = int(value)
                # Clamp input to 16-bit
                clamped_val = self._clamp_16bit(val)
                self.memory[self.input_dest_addr] = clamped_val
                self.touched_memory.add(self.input_dest_addr)

                self.input_dest_addr += 1
                self.input_needed -= 1

                # Only advance PC if we are done with all inputs for this instruction
                if self.input_needed == 0:
                    self.pc += 1

                return True
            except ValueError:
                return False
        return False

    def step(self):
        """
        Executes a single instruction cycle (Fetch -> Decode -> Execute).

        Updates PC, Memory, and flags.
        """
        if self.is_finished or self.input_needed > 0:
            return

        # Fetch Instruction
        if self.pc not in self.instructions:
            self.last_error = f"End of program or invalid PC: {self.pc}"
            self.is_finished = True
            return

        instr_data = self.instructions[self.pc]
        line = instr_data["text"]

        # 1. Tokenize (Opcode + CSV Arguments)
        parts = line.split(maxsplit=1)
        opcode = parts[0].upper()
        args = []
        if len(parts) > 1:
            # Better splitting: split by comma, then strip whitespace
            args = [arg.strip() for arg in parts[1].split(",")]

        # Default next instruction address
        next_pc = self.pc + 1

        try:
            # --- DATA MOVEMENT ---
            if opcode == "MOV":
                val = self.resolve_value(args[1])
                self.set_value(args[0], val)

            # --- ARITHMETIC ---
            elif opcode in ["ADD", "SUB", "MUL", "DIV"]:
                # Load values as signed integers for proper math
                val1 = self.resolve_value(args[1])
                val2 = self.resolve_value(args[2])

                res = 0
                if opcode == "ADD":
                    res = val1 + val2
                elif opcode == "SUB":
                    res = val1 - val2
                elif opcode == "MUL":
                    res = val1 * val2
                elif opcode == "DIV":
                    if val2 == 0:
                        raise ValueError("Division by zero")
                    # Integer Division (Truncated)
                    res = int(val1 / val2)

                self.set_value(args[0], res)

            # --- INPUT/OUTPUT ---
            elif opcode == "IN":
                target_addr = self.resolve_write_target(args[0])
                count = 1
                if len(args) > 1:
                    count = self.resolve_value(args[1])

                if count > 0:
                    self.input_needed = count
                    self.input_dest_addr = target_addr
                    # Do NOT advance PC yet; waiting for GUI input
                    return

            elif opcode == "OUT":
                # Determine start address for output array/variable
                start_addr = 0
                raw_arg = args[0].strip().upper()

                if raw_arg.startswith("(") and raw_arg.endswith(")"):
                    inner = raw_arg[1:-1]
                    ptr_loc = self.resolve_symbol(inner)
                    start_addr = self.memory[ptr_loc]
                else:
                    start_addr = self.resolve_symbol(raw_arg)

                count = 1
                if len(args) > 1:
                    count = self.resolve_value(args[1])

                line_out = []
                for i in range(count):
                    curr = start_addr + i
                    if curr < len(self.memory):
                        # Convert to signed for display
                        val_signed = self._to_signed(self.memory[curr])
                        line_out.append(str(val_signed))

                if line_out:
                    self.output_buffer.append(" ".join(line_out))

            # --- CONTROL FLOW ---
            elif opcode == "BEQ":
                val1 = self.resolve_value(args[0])
                val2 = self.resolve_value(args[1])
                label = args[2].upper()

                if val1 == val2:
                    if label in self.labels:
                        next_pc = self.labels[label]
                    else:
                        raise ValueError(f"Unknown label: {label}")

            elif opcode == "BGT":
                val1 = self.resolve_value(args[0])
                val2 = self.resolve_value(args[1])
                label = args[2].upper()

                # Comparison uses signed logic (e.g. 5 > -5 is True)
                if val1 > val2:
                    if label in self.labels:
                        next_pc = self.labels[label]
                    else:
                        raise ValueError(f"Unknown label: {label}")

            # --- SUBROUTINES ---
            elif opcode == "JSR":
                label = args[0].upper()
                # Push Return Address (next_pc) to stack
                # Note: SP moves DOWN
                self.memory[self.sp] = self._clamp_16bit(next_pc)
                self.touched_memory.add(self.sp)
                self.sp -= 1

                if label in self.labels:
                    next_pc = self.labels[label]
                else:
                    raise ValueError(f"Unknown label: {label}")

            elif opcode == "RTS":
                self.sp += 1
                if self.sp >= len(self.memory):
                    raise ValueError("Stack underflow")
                # Pop return address from stack
                next_pc = self.memory[self.sp]

            # --- SYSTEM ---
            elif opcode == "STOP":
                self.is_finished = True
                # Handle multiple optional arguments for debug printing: STOP A, B, C
                if args:
                    results = []
                    for arg in args:
                        val = self.resolve_value(arg)
                        results.append(str(val))
                    self.output_buffer.append("STOP: " + ", ".join(results))
                else:
                    self.output_buffer.append("STOP")

            # Final 16-bit wrap for PC to ensure it stays valid
            self.pc = self._clamp_16bit(next_pc)

        except Exception as e:
            self.last_error = f"Error line {instr_data['line_no']}: {str(e)}"
            self.is_finished = True
            # For debugging, print to console if needed
            print(self.last_error)
