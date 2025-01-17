const int ROWS = 21;  // Adjust the number of rows as needed
const int COLS = 9;  // Adjust the number of columns as needed
const int TUPLE_SIZE = 3;  // Size of the RGB tuple

const int BLUE_LED = 7;
const int RED_LED = 6;

int get_color_array(String data){
  // Convert the received string back to 2D array format
    String rows[ROWS];
    int rowIdx = 0;

    for (int i = 0; i < data.length(); i++) {
      if (data[i] == ';') {
        rowIdx++;
      } else {
        rows[rowIdx] += data[i];
      }
    }

    int array[ROWS][COLS][TUPLE_SIZE];
    for (int i = 0; i < ROWS; i++) {
      String tuples[COLS];
      int tupIdx = 0;
      for (int j = 0; j < rows[i].length(); j++) {
        if (rows[i][j] == '|') {
          tupIdx++;
        } else {
          tuples[tupIdx] += rows[i][j];
        }
      }

      for (int k = 0; k < COLS; k++) {
        int values[TUPLE_SIZE];
        int valIdx = 0;
        String val = "";
        for (int l = 0; l < tuples[k].length(); l++) {
          if (tuples[k][l] == ',') {
            values[valIdx] = val.toInt();
            valIdx++;
            val = "";
          } else {
            val += tuples[k][l];
          }
        }
        values[valIdx] = val.toInt();
        for (int m = 0; m < TUPLE_SIZE; m++) {
          array[i][k][m] = values[m];
        }
      }
    }
    Serial.print(array[0][0][0]);
    return array;
}

void setup() {

  pinMode(BLUE_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);

  Serial.begin(9600);
  while (!Serial) {
    ; // Wait for serial port to connect. Needed for native USB
  }
}

void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');  // Read data from serial until newline character

    int color_array = get_color_array(data);
    //Serial.print(color_array[0][0][0])

    // Now you have the array back in integer format, you can use it as needed

    digitalWrite(BLUE_LED, HIGH);
    digitalWrite(RED_LED, LOW);
  }

  else{
    digitalWrite(BLUE_LED, LOW);
    digitalWrite(RED_LED, HIGH);
  }

}
