import { useState, useRef } from "react";
import { View, Text, TouchableOpacity, TextInput, StyleSheet, Alert, ScrollView } from "react-native";
import { CameraView, useCameraPermissions } from "expo-camera";
import * as Location from "expo-location";
import axios from "axios";

// ⚠️ Replace with YOUR computer's LAN IP from `ipconfig` (keep the port :5000)
const API_BASE = "http://192.168.0.103:5000/api";

export default function CaptureScreen() {
  const [permission, requestPermission] = useCameraPermissions();
  const [locationPermission, requestLocationPermission] = Location.useForegroundPermissions();
  const [photo, setPhoto] = useState<string | null>(null);
  const [notes, setNotes] = useState("");
  const [location, setLocation] = useState<Location.LocationObject | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const cameraRef = useRef<CameraView>(null);

  if (!permission) return <View />;
  if (!permission.granted) {
    return (
      <View style={styles.center}>
        <Text style={styles.text}>Camera access is needed to submit artifacts.</Text>
        <TouchableOpacity style={styles.button} onPress={requestPermission}>
          <Text style={styles.buttonText}>Grant permission</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const login = async () => {
    try {
      const res = await axios.post(`${API_BASE}/auth/login`, { email, password });
      setToken(res.data.token);
      Alert.alert("Logged in", `Welcome, ${res.data.user.email}`);
    } catch (err) {
      Alert.alert("Login failed", "Check your email/password");
    }
  };

  const takePhoto = async () => {
    if (!cameraRef.current) return;
    const result = await cameraRef.current.takePictureAsync({ base64: true, quality: 0.5 });
    setPhoto(`data:image/jpeg;base64,${result.base64}`);

    if (!locationPermission?.granted) {
      await requestLocationPermission();
    }
    try {
      const loc = await Location.getCurrentPositionAsync({});
      setLocation(loc);
    } catch (err) {
      console.log("Location unavailable:", err);
    }
  };

  const submit = async () => {
    if (!photo || !token) return;
    setSubmitting(true);
    try {
      await axios.post(
        `${API_BASE}/submissions`,
        {
          photo_url: photo,
          latitude: location?.coords.latitude,
          longitude: location?.coords.longitude,
          notes,
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      Alert.alert("Submitted!", "Your artifact was uploaded successfully.");
      setPhoto(null);
      setNotes("");
    } catch (err) {
      Alert.alert("Submission failed", "Check the console for details.");
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  if (!token) {
    return (
      <View style={styles.center}>
        <Text style={styles.title}>Heritage Trace — Volunteer Login</Text>
        <TextInput style={styles.input} placeholder="Email" value={email} onChangeText={setEmail} autoCapitalize="none" />
        <TextInput style={styles.input} placeholder="Password" value={password} onChangeText={setPassword} secureTextEntry />
        <TouchableOpacity style={styles.button} onPress={login}>
          <Text style={styles.buttonText}>Log in</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (photo) {
    return (
      <ScrollView contentContainerStyle={styles.center}>
        <Text style={styles.title}>Confirm submission</Text>
        <TextInput
          style={styles.input}
          placeholder="Notes (optional)"
          value={notes}
          onChangeText={setNotes}
          multiline
        />
        <Text style={styles.text}>
          Location: {location ? `${location.coords.latitude.toFixed(4)}, ${location.coords.longitude.toFixed(4)}` : "..."}
        </Text>
        <TouchableOpacity style={styles.button} onPress={submit} disabled={submitting}>
          <Text style={styles.buttonText}>{submitting ? "Submitting..." : "Submit artifact"}</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.button, styles.secondary]} onPress={() => setPhoto(null)}>
          <Text style={styles.buttonText}>Retake</Text>
        </TouchableOpacity>
      </ScrollView>
    );
  }

  return (
    <View style={{ flex: 1 }}>
      <CameraView ref={cameraRef} style={{ flex: 1 }} facing="back" />
      <TouchableOpacity style={styles.captureButton} onPress={takePhoto}>
        <Text style={styles.buttonText}>📸 Capture artifact</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: "center", alignItems: "center", padding: 20, gap: 10 },
  title: { fontSize: 20, fontWeight: "bold", marginBottom: 10 },
  text: { fontSize: 14, marginBottom: 10, textAlign: "center" },
  input: { borderWidth: 1, borderColor: "#ccc", borderRadius: 8, padding: 10, width: "100%" },
  button: { backgroundColor: "#2563eb", padding: 14, borderRadius: 8, width: "100%", alignItems: "center", marginTop: 10 },
  secondary: { backgroundColor: "#6b7280" },
  buttonText: { color: "white", fontWeight: "bold" },
  captureButton: {
    position: "absolute", bottom: 40, alignSelf: "center",
    backgroundColor: "#2563eb", paddingVertical: 14, paddingHorizontal: 24, borderRadius: 30,
  },
});