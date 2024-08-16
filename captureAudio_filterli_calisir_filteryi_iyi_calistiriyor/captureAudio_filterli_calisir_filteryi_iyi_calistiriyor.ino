#include <Arduino.h>
#include <driver/i2s.h>





#define I2S_WS 32
#define I2S_SCK 26
#define I2S_SD 33

//#define ALPHA 0.01



// Filter coefficients generated from Python (example values, replace with actual coefficients)
/*
const int order = 2;
const float b[] = {0.23650403, 0.4711346,  0.23650403};  // Numerator coefficients
const float a[] = {1.,         1.19660193, 0.78903929};   // Denominator coefficients

// State variables for filter
float w[5] = {0, 0, 0, 0, 0};
*/

double x[] = {0,0,0};
double y[] = {0,0,0};
int k = 0;






void setupMic()
{


  esp_err_t err;


  i2s_config_t i2s_config = {
  .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
  .sample_rate = 16000,
  .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT, 
  .channel_format =  I2S_CHANNEL_FMT_ONLY_LEFT,
  .communication_format = i2s_comm_format_t(I2S_COMM_FORMAT_I2S | I2S_COMM_FORMAT_I2S_MSB),
  .intr_alloc_flags =  0,
  .dma_buf_count = 8,
  .dma_buf_len = 64,
  .use_apll = false,
  .tx_desc_auto_clear = true,
  .fixed_mclk =  0
  
  };


    i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num =  I2S_SD
  };


  // Configuring the I2S driver and pins.
  // This function must be called before any I2S driver read/write operations.
  err = i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
  if (err != ESP_OK) {
    Serial.printf("Failed installing driver: %d\n", err);
    while (true);
  }

  err = i2s_set_pin(I2S_NUM_0, &pin_config);
  if (err != ESP_OK) {
    Serial.printf("Failed setting pin: %d\n", err);
    while (true);
  }


  Serial.println("I2S driver installed.");
}






void setup() {
  Serial.begin(115200);

  delay(2000);
  Serial.println("Setting up mic");
  setupMic();
  Serial.println("Mic setup completed"); 

}




void loop() {
  
  int16_t buffer[64];
  size_t bytes_read;

  static double y_prev = 0; // Previous output sample (initialize to 0)

  i2s_read(I2S_NUM_0, &buffer, sizeof(buffer), &bytes_read, portMAX_DELAY);

  for (int i = 0; i < bytes_read / 2; i++) {
  
  x[0] = buffer[i];

  double b[] = {0.00242481, 0.00484962, 0.00242481};
  double a[] = { 1.85595643,  -0.86565567};
    y[0] = a[0]*y[1] + a[1]*y[2] +
               b[0]*x[0] + b[1]*x[1] + b[2]*x[2];


  //Serial.println(x[0]);
  //Serial.print(" ");
  Serial.println(y[0]);
 
  /*
  if(k % 3 ==0)
  {
    // This extra conditional statement is here to reduce
    // the number of times the data is sent through the serial port
    // because sending data through the serial port
    // messes with the sampling frequency
    
    // For the serial monitor
   /*
    Serial.print(x[0]);
    Serial.print(" ");
    Serial.println(y[0]);
  }
  qeqwe
  */

  delay(1); // Wait 1ms
  for(int j = 1; j >= 0; j--){
    x[j+1] = x[j]; // store xi
    y[j+1] = y[j]; // store yi
  }
  
  k = k+1;



   /* Filter
   
    // Apply the low-pass filter
    float x = buffer[i];  // Current input sample
    float y = ALPHA * x + (1 - ALPHA) * y_prev;  // Filtered output
    y_prev = y;  // Update previous output
    
    

    Serial.println((int16_t)y);
   */   

    //Serial.println(buffer[i]);


  }

   /*   Cauer Filter   
    float x = buffer[i];

    // Apply the Elliptic filter
    float y = b[0] * x + w[0];
    for (int j = 1; j < 5; j++) {
      w[j - 1] = b[j] * x + w[j] - a[j] * y;
    }
    w[4] = -a[4] * y;

    // Print the filtered sample
    Serial.println((int16_t)y);
  */
  
}
