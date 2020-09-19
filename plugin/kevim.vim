""""""""""""""""""slime functinality"""""""""""""""""

noremap <SID>Operator :<c-u>set opfunc=KevimTermSend<cr>g@

noremap <unique> <script> <silent> <Plug>KevimRegionSend :<c-u>call KevimTermSend(visualmode(), 1)<cr>
noremap <unique> <script> <silent> <Plug>KevimMotionSend <SID>Operator
noremap <unique> <script> <silent> <Plug>KevimParagraphSend <SID>Operatorip

let g:kevim_term_width = 90

nmap sm <Plug>KevimMotionSend
nmap sp <Plug>KevimParagraphSend
xmap sp <Plug>KevimRegionSend

""""""""""""""""" buffer switching """""""""""""""""""

noremap <silent> <C-h> :call KevimBChange("prev")<CR>
noremap <silent> <C-l> :call KevimBChange("next")<CR>
noremap <silent> <C-k> :call KevimBChange("delete")<CR>

""""""""""""""""" etc """""""""""""""""""""""""""""
noremap sf :KevimFormatIndent<CR>
