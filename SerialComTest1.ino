String data = "";

void setup() { 
	Serial.begin(9600); 
	//Serial.setTimeout(1); 
  pinMode(7, OUTPUT);
  pinMode(6, OUTPUT);
} 
bool blue = true;
void loop() { 
	  if (Serial.available()) {
    data = Serial.readStringUntil('\n');
    blue = true;
  }else{
    blue = false;
  }

  if(data == "blue"){
      blue = true;
    }

  if(blue){
    digitalWrite(6, LOW);
    digitalWrite(7, HIGH);
  }
  if(!blue){
    digitalWrite(6, HIGH);
    digitalWrite(7, LOW);
  }

} 









/*void setup() { 
	Serial.begin(9600); 
	//Serial.setTimeout(1); 
  pinMode(7, OUTPUT);
  pinMode(6, OUTPUT);
} 
bool bruh = false;
bool breh = false;
void loop() { 
	  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    bruh = true;
    if(data == "blue"){
      breh = true;
    }
  }
  if(bruh){
    digitalWrite(6, HIGH);
  }
  if(breh){
    digitalWrite(7, HIGH);
  }

} */
