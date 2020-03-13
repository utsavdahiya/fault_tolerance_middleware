import com.fasterxml.jackson.databind.util.JSONPObject;
import org.springframework.messaging.Message;
import org.springframework.messaging.simp.stomp.StompHeaders;
import org.springframework.messaging.simp.stomp.StompSession;
import org.springframework.messaging.simp.stomp.StompSessionHandlerAdapter;

import java.lang.reflect.Type;

public class MyStompSessionHandler extends StompSessionHandlerAdapter {
    @Override
    public void afterConnected(StompSession session, StompHeaders connectedHeaders) {
        session.subscribe("", this);
        //  session.subscribe("/post", this);
        //session.send("", "pls chal jaa");
        System.out.println("SMH");
        System.out.println("yolo" + connectedHeaders.toString());
    }
    @Override
    public void handleFrame(StompHeaders headers, Object payload) {
        Message msg = (Message) payload;
        System.out.println("yolo" + payload.toString());
        System.out.println("Received : " + msg.toString());
    }

    @Override
    public Type getPayloadType(StompHeaders headers) {
        return String.class;
    }
}
