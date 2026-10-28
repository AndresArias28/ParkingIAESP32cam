import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';
import 'parking_station.dart';

Future<void> main() async{
  WidgetsFlutterBinding.ensureInitialized();// Ensures that Flutter's widget binding is initialized before Firebase is initialized.
  // This is crucial for asynchronous operations like Firebase.initializeApp().

  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );

  runApp(const MyApp());
}

//calse MyApp - widget que no necesita manejar un estado propio mutable
class MyApp extends StatelessWidget { //sirve cuando la información del widget no cambia internamente.
  const MyApp({super.key}); //Constructor de myApp, utiliza super.key para pasar la clave al constructor de la clase base StatelessWidget. porque StatelessWidget requiere una clave para identificar de manera única el widget en el árbol de widgets. 

  // This widget is the root of your application.
  @override
  //construir el widget, el método build es llamado cada vez que el widget necesita ser renderizado.
  Widget build(BuildContext context) {
    //BuildContext representa el contexto en el que se encuentra el widget en el árbol de widgets. Proporciona información sobre la ubicación del widget y permite acceder a otros widgets y recursos en el árbol.
    return MaterialApp(  //MaterialAPP representa la aplicación en sí y proporciona una serie de características y configuraciones para la aplicación, como el tema, las rutas, etc.
      
      theme: ThemeData(
        // This is the theme of your application.
        colorScheme: ColorScheme.fromSeed(seedColor: const Color.fromARGB(255, 25, 8, 54)),
      ),
      //MyHomePage es el contruscotr de la clase MyHomePage, que es un widget que representa la página principal de la aplicación. Se pasa un título como argumento al constructor de MyHomePage.
      home: const ParkingStation(),
    );
  }
}

