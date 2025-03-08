
# syntax.md

## SPL Syntax Guide

SPL (Swahili Programming Language) follows a simple and intuitive syntax inspired by natural Swahili expressions.

### 1. **Variables**
   - **Declaration:**
     ```spl
     jina = "Amina"
     umri = 25
     ```

### 2. **Conditional Statements**
   - **If-Else Structure:**
     ```spl
     kama (umri > 18) {
         kitoa("Wewe ni mtu mzima.")
     } sivyo {
         kitoa("Bado mdogo.")
     }
     ```

### 3. **Loops**
   - **For Loop:**
     ```spl
     kwa i katika anuwai(1, 5) {
         kitoa(i)
     }
     ```
   - **While Loop:**
     ```spl
     wakati (umri < 30) {
         kitoa("Bado kijana.")
         umri = umri + 1
     }
     ```

### 4. **Functions**
   - **Defining Functions:**
     ```spl
     kazi salamu(jina) {
         kitoa("Habari " + jina)
     }
     ```
   - **Calling a Function:**
     ```spl
     salamu("Amina")
     ```

### 5. **Comments**
   - **Single-line Comment:**
     ```spl
     # Hii ni maoni moja ya mstari
     ```
   - **Multi-line Comment:**
     ```spl
     /*
     Hii ni maoni ya mistari mingi
     inayoelezea programu hii.
     */
     ```

