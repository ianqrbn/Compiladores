.data
var_phoenix_number: .word 0
var_var1: .word 0
var_var2: .word 0
var_cavalo: .word 0

.text
.globl main
main:
    lw $t0, var_var1
    subu $sp, $sp, 4
    sw $t0, ($sp)
    li $t0, 10
    subu $sp, $sp, 4
    sw $t0, ($sp)
    lw $t0, ($sp)
    addu $sp, $sp, 4
    lw $t1, ($sp)
    addu $sp, $sp, 4
    sw $t0, var_var1
    subu $sp, $sp, 4
    sw $t0, ($sp)
    lw $t0, ($sp)
    addu $sp, $sp, 4
    lw $t0, var_var2
    subu $sp, $sp, 4
    sw $t0, ($sp)
    li $t0, 1
    subu $sp, $sp, 4
    sw $t0, ($sp)
    lw $t0, ($sp)
    addu $sp, $sp, 4
    lw $t1, ($sp)
    addu $sp, $sp, 4
    sw $t0, var_var2
    subu $sp, $sp, 4
    sw $t0, ($sp)
    lw $t0, ($sp)
    addu $sp, $sp, 4
    lw $t0, var_phoenix_number
    subu $sp, $sp, 4
    sw $t0, ($sp)
    li $t0, 142857
    subu $sp, $sp, 4
    sw $t0, ($sp)
    lw $t0, ($sp)
    addu $sp, $sp, 4
    lw $t1, ($sp)
    addu $sp, $sp, 4
    sw $t0, var_phoenix_number
    subu $sp, $sp, 4
    sw $t0, ($sp)
    lw $t0, ($sp)
    addu $sp, $sp, 4
    lw $t0, var_phoenix_number
    subu $sp, $sp, 4
    sw $t0, ($sp)
    lw $t0, ($sp)
    addu $sp, $sp, 4
    sub $t0, $t0, 1
    sw $t0, var_phoenix_number
    subu $sp, $sp, 4
    sw $t0, ($sp)
    lw $t0, ($sp)
    addu $sp, $sp, 4
    lw $t0, var_var1
    subu $sp, $sp, 4
    sw $t0, ($sp)
    lw $t0, var_var2
    subu $sp, $sp, 4
    sw $t0, ($sp)
    lw $t0, ($sp)
    addu $sp, $sp, 4
    lw $t1, ($sp)
    addu $sp, $sp, 4
    sw $t0, var_var1
    subu $sp, $sp, 4
    sw $t0, ($sp)
    li $t0, 55
    subu $sp, $sp, 4
    sw $t0, ($sp)
    lw $t1, ($sp)
    addu $sp, $sp, 4
    lw $t0, ($sp)
    addu $sp, $sp, 4
    add $t0, $t0, $t1
    subu $sp, $sp, 4
    sw $t0, ($sp)
    lw $t0, ($sp)
    addu $sp, $sp, 4
    lw $t0, var_phoenix_number
    subu $sp, $sp, 4
    sw $t0, ($sp)
    li $t0, 142857
    subu $sp, $sp, 4
    sw $t0, ($sp)
    lw $t1, ($sp)
    addu $sp, $sp, 4
    lw $t0, ($sp)
    addu $sp, $sp, 4
    seq $t0, $t0, $t1
    subu $sp, $sp, 4
    sw $t0, ($sp)
    lw $t0, ($sp)
    addu $sp, $sp, 4
    beq $t0, $zero, L_ELSE_1
    lw $t0, var_cavalo
    subu $sp, $sp, 4
    sw $t0, ($sp)
    lw $t0, var_var1
    subu $sp, $sp, 4
    sw $t0, ($sp)
    lw $t0, ($sp)
    addu $sp, $sp, 4
    lw $t1, ($sp)
    addu $sp, $sp, 4
    sw $t0, var_cavalo
    subu $sp, $sp, 4
    sw $t0, ($sp)
    lw $t0, var_var2
    subu $sp, $sp, 4
    sw $t0, ($sp)
    lw $t1, ($sp)
    addu $sp, $sp, 4
    lw $t0, ($sp)
    addu $sp, $sp, 4
    sub $t0, $t0, $t1
    subu $sp, $sp, 4
    sw $t0, ($sp)
    lw $t0, ($sp)
    addu $sp, $sp, 4
    j L_ENDIF_2
L_ELSE_1:
L_ENDIF_2:
    li $v0, 10
    syscall
