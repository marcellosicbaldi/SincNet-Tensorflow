class SincConv2D(Layer):

    def __init__(
            self,
            N_filt,
            Filt_dim,
            fs,
            padding="SAME",
            **kwargs):
        self.N_filt = N_filt
        self.Filt_dim = Filt_dim
        self.fs = fs
        self.padding = padding

        super(SincConv2D, self).__init__(**kwargs)

    def build(self, input_shape):
        # The filters are trainable parameters.
        self.filt_b1 = self.add_weight(
            name='filt_b1',
            shape=(self.N_filt, 1),
            initializer='uniform',
            trainable=True)
        self.filt_band = self.add_weight(
            name='filt_band',
            shape=(self.N_filt, 1),
            initializer='uniform',
            trainable=True)

        low_freq = 4
        high_freq = 38

        # Random initialization between low_freq and high_freq
        low_hz = np.expand_dims(np.random.uniform(low_freq, high_freq, self.N_filt), axis = -1)

        hz_points = np.linspace(low_freq, high_freq, self.N_filt+1)
        band_hz = np.expand_dims(np.diff(hz_points), axis = -1)

        t_right = tf.constant(tf.linspace(1.0, (self.Filt_dim - 1) / 2, int((self.Filt_dim - 1) / 2)) / self.fs, tf.float32)
        self.T_Right = tf.tile(tf.expand_dims(t_right, axis=0), (self.N_filt, 1))

        n = tf.linspace(0, self.Filt_dim - 1, self.Filt_dim)
        window = 0.54 - 0.46 * tf.cos(2 * math.pi * n / self.Filt_dim)
        window = tf.cast(window, tf.float32)
        self.Window = tf.tile(tf.expand_dims(window, axis=0), (self.N_filt, 1))

        # This sets the weights of the layer (filt_b1 and filt_band) from a list of NumPy arrays 
        self.set_weights([low_hz/fs, band_hz/fs]) 

        super(SincConv2D, self).build(input_shape)  # Be sure to call this at the end

    def call(self, x, **kwargs):
        
        low_freq = 4
        high_freq = 38
        # min_band = 5
        
        # Get lower and upper cutoff frequencies of the filters.
        filt_beg_freq = tf.abs(self.filt_b1)   # lower cutoff frequency

        # The upper cutoff is imposed to be always greater than the lower cutoff by filt_band
        # filt_band is a learnable parameter!! --> Instead of learning the upper cutoff I learn the pass bandwidth
        filt_end_freq = filt_beg_freq + tf.abs(self.filt_band)# + min_band/self.fs # upper cutoff frequency
        
        low_pass1 = self.low_pass_(filt_beg_freq*fs)
        low_pass2 = self.low_pass_(filt_end_freq*fs)
        band_pass = (low_pass2 - low_pass1)
        band_pass = band_pass / tf.reduce_max(band_pass, axis=1, keepdims=True)
        windowed_band_pass = band_pass * self.Window
        
        filters = tf.transpose(windowed_band_pass)
        filters = tf.reshape(filters, (1, self.Filt_dim, 1, self.N_filt))

        # Do the convolution.
        out = tf.nn.conv2d(
            x,
            filters=filters,
            strides = 1,
            padding=self.padding
        )

        return out

    def low_pass_(self, fc):
        y_right = tf.sin(math.pi * 2*fc*self.T_Right) / (math.pi * 2*fc*self.T_Right)
        y_left = tf.reverse(y_right, [1])
        y = tf.concat([y_left, tf.ones((self.N_filt, 1)), y_right], axis=1)
        return 2*fc*y

    def compute_output_shape(self, input_shape):
        new_size = conv_utils.conv_output_length(
            input_shape[2],
            self.kernel_size,
            padding="same",
            stride=1)
        return (input_shape[:2]) + (new_size,) + (self.N_filt,)
