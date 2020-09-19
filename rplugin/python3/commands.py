import pynvim
from itertools import cycle

#from pynvim import attach
#nvim = attach('socket', path='/tmp/nvim')
#

@pynvim.plugin
class Kevim(object):
    def __init__(self, nvim):
        self.nvim = nvim

    def echom(self, m):
        self.nvim.command('echom "{}"'.format(str(m).replace('"', '""')))

    def next_buf(self, buf):
        it = iter(cycle(self.nvim.buffers))
        cur = next(it)
        # cycle to current buf
        while buf != cur:
            cur = next(it)
        return next(it)

    def prev_buf(self, buf):
        it = iter(cycle(self.nvim.buffers))
        cur = next(it)
        # cycle to current buf
        while buf != cur:
            cur = next(it)

        for _ in range(0, len(self.nvim.buffers) - 1):
            cur = next(it)

        return cur

    def term_jobid(self):
        AUTO_WIDTH = 80

        term_buffers = [w.buffer for w in self.nvim.windows if w.buffer.name.startswith('term://')]

        if len(term_buffers) > 1: # multiple buffers, give choice
            msg = "select buffer: "
            for b in term_buffers:
                msg += "job {}: {}\n".format(b.options.get('channel'), b.name.split(':')[-1])
            return self.nvim.call('input', msg)
        elif len(term_buffers) < 1: # create buffer
            term_cmd = self.nvim.call('input', 'enter repl command: ')
            self.nvim.command('vsplit')
            self.nvim.current.window.width = self.nvim.eval('g:kevim_term_width') or AUTO_WIDTH
            self.nvim.command('terminal {}'.format(term_cmd))
            self.nvim.input('<C-\><C-n><C-w>l')
            return self.term_jobid()
        else: # base case. boom.
            return term_buffers[0].options.get('channel')

    def get_motion(self, args):
        self.nvim.command('let sel_save = &selection')
        self.nvim.command('let cb_save = &clipboard')
        self.nvim.command('let reg_save = @@')
        self.nvim.command('let &selection = "inclusive"')
        self.echom(args)

        if len(args) > 1 and args[1]: # Invoked from Visual mode, use '< and '> marks.
            self.nvim.command('silent exe "normal! `<{}`>y"'.format(args[0]))
        elif args[0] == 'block':
            self.nvim.command('silent exe "normal! `[\<C-V>`]\y"')
        elif args[0] == 'line':
            self.nvim.command('exe "normal! \'[V\']y"')
        else:
            self.nvim.command('exe "normal! `[v`]y"')

        text = self.nvim.eval('@@')
        self.nvim.command('let &selection = sel_save')
        self.nvim.command('let &clipboard = cb_save')
        self.nvim.command('let @@ = reg_save')
        return text

    @pynvim.function('KevimTermSend', sync=True)
    def send_function(self, args):
        text = self.get_motion(args)
        send_to = self.term_jobid()
        self.nvim.call('chansend', int(send_to), text.split('\n'))


    @pynvim.function('KevimBChange', sync=True)
    def next_buffer(self, args):
        if args[0] == 'next':
            delta = lambda b: self.next_buf(b)
        elif args[0] == 'prev':
            delta = lambda b: self.prev_buf(b)
        elif args[0] == 'delete':
            delete_buff = self.nvim.current.buffer
            self.nvim.call('KevimBChange', 'prev')
            if self.nvim.current.buffer == delete_buff:
                self.nvim.input('ZZ')
            elif delete_buff.name.startswith('term://'):
                self.nvim.command('bdelete! {}'.format(delete_buff.number))
            else:
                self.nvim.command('bdelete {}'.format(delete_buff.number))
            return

        b = delta(self.nvim.current.buffer)

        while (b.name.startswith('term://') or
                not b.valid or
                b.options.get('filetype') == 'netrw' or
                b.options.get('filetype') == ''):
            b = delta(b)

        self.nvim.current.buffer = b

    # this "linter" is not ideal but should suit my temporary needs
    @pynvim.command('KevimFormatIndent', sync=True, nargs='*', range='')
    def format_cmd(self, args, r):
        save_pos = self.nvim.call('getcurpos')
        [start, end] = r

        self.nvim.input('<Esc>{}gg'.format(start))

        for i in range(start, end + 1):
            self.nvim.input('0i<CR><Esc>kddj')

        self.nvim.async_call('setpos', '.', save_pos)


    def test(self):

        from pynvim import attach

        nvim = attach('socket', path='/tmp/nvim')

        

